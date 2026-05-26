from fastapi import Depends
from sqlalchemy import select, union_all, literal, Integer
from sqlalchemy.orm import aliased, Session, joinedload
from collections  import defaultdict
from src.models import Contact, Interest, interest, interest_sectors
from src.repositories.contact_repository import ContactRepository
import json


class InterestRepository():
    __session: Session

    def __init__(self, session: Session = Depends(Session)):
        self.__session = session

    def get_interest_from_id(self, id: int) -> Interest:
        interest = self.__session.query(Interest).filter(Interest.id == id).first()
        return interest
    
    def get_interest_from_name(self, name: str) -> Interest:
        interest = self.__session.query(Interest).filter(Interest.name == name).first()
        return interest

    def get_all_interests(self) -> list[Interest]:
        interests = self.__session.query(Interest).all()
        return interests
    
    def get_interests_for_contact(self, contact_id: int) -> list[Interest]:
        contact_repository = ContactRepository(self.__session)
        contact = contact_repository.get_contact(contact_id)
        
        interests = (
            self.__session.query(Interest)
            .join(interest_sectors, Interest.id == interest_sectors.c.interest_id)
            .filter(interest_sectors.c.sector_id == contact.sector_id)
            .all()
        )
        return interests
    
    def extract_interests_from_json(self, user_json) -> dict[str, float]:
        """
        Garde la structure complète {"hair_care": 0.1} pour conserver le score.
        """
        if not user_json:
            return {}
        if isinstance(user_json, str):
            try:
                return json.loads(user_json)
            except json.JSONDecodeError:
                return {}
        return user_json

    def build_indexes(self, interests: list[Interest]):
        """
        Construit des index en mémoire (dictionnaires et listes) à partir des 
        objets Interest du secteur pour éviter de refaire des requêtes SQL.
        """
        # Index pour retrouver un objet Interest par nom, ID et regroupement key Parent - value Enfants
        by_name: dict[str, Interest] = {}
        by_id: dict[int, Interest] = {}
        children: dict[int, list[Interest]] = defaultdict(list)
        
        roots: list[Interest] = []

        # Remplissage des dict
        for item in interests:
            by_name[item.name] = item
            by_id[item.id] = item
            
            if item.parent is not None:
                children[item.parent].append(item)
            else:
                roots.append(item)

        return by_name, by_id, children, roots


    def _compute_propagated_scores(
        self, 
        user_interests_dict: dict[str, float], 
        by_name: dict[str, Interest], 
        children: dict[int, list[Interest]]
        ) -> dict[str, float]:
        """Calcule les scores initiaux et propage les bonus aux enfants et aux frères."""
        result_scores = {}

        # Initialisation des scores explicites
        for name, score in user_interests_dict.items():
            if name in by_name:
                result_scores[name] = score

        # Propagation des bonus
        for name, score in user_interests_dict.items():
            if name not in by_name:
                continue
                
            node = by_name[name]
            
            # Depuis parent vers enfants (50% de la force, max 0.2)
            for c in children.get(node.id, []):
                bonus_parent = min(score * 0.5, 0.2)
                result_scores[c.name] = result_scores.get(c.name, 0.0) + bonus_parent

            # Depuis siblings (20% de la force, max 0.1)
            if node.parent is not None:
                for s in children.get(node.parent, []):
                    if s.id != node.id:
                        bonus_sibling = min(score * 0.2, 0.1)
                        result_scores[s.name] = result_scores.get(s.name, 0.0) + bonus_sibling

        # Remise à 1.0 si score dépassant
        for name in result_scores:
            result_scores[name] = min(result_scores[name], 1.0)

        return result_scores

    def _sort_and_filter_interests(
        self, 
        result_scores: dict[str, float], 
        by_name: dict[str, Interest], 
        roots: list[Interest]
        ) -> list[Interest]:
        """Filtre les intérêts pour exclure les roots, puis les trie par score décroissant."""
        root_names = {r.name for r in roots}

        # Récupère uniquement les objets non-roots présents dans les scores
        matched_interest_objects = [
            by_name[name] for name in result_scores.keys() 
            if name not in root_names
        ]

        # Tri décroissant sur le score, puis alphabétique sur le nom
        return sorted(
            matched_interest_objects, 
            key=lambda interest: (-result_scores[interest.name], interest.name)
        )


    def get_prioritized_interests(self, user_json, interests_du_secteur):
        """
        Calcule les scores cumulés et plafonnés des intérêts d'un contact 
        en fonction des relations de parenté et d'un dictionnaire de scores initiaux.
        Retourne la liste des objets intérêts non-roots triés, ainsi que la liste des roots.
        """
        user_interests_dict = self.extract_interests_from_json(user_json)
        by_name, _, children, roots = self.build_indexes(interests_du_secteur)

        result_scores = self._compute_propagated_scores(user_interests_dict, by_name, children)

        sorted_non_roots = self._sort_and_filter_interests(result_scores, by_name, roots)

        return sorted_non_roots, roots

        """
        Calcule les scores cumulés et plafonnés des intérêts d'un contact 
        en fonction des relations de parenté et d'un dictionnaire de scores initiaux.
        Retourne la liste des noms d'intérêts triée par priorité décroissante.
        """
        # Étape 0 : Extraction sécurisée du dictionnaire de scores de l'utilisateur {"nom": score}
        user_interests_dict = self.extract_interests_from_json(user_json)
        
        # Génération des index optimisés en mémoire pour le secteur du contact
        by_name, by_id, children, roots = self.build_indexes(interests_du_secteur)

        # Ce dictionnaire stockera les scores finaux accumulés : {"nom_interet": score_cumule}
        result_scores = {}

        # =========================================================================
        # ÉTAPE 1 : Initialisation des scores explicites
        # =========================================================================
        # On commence par attribuer aux intérêts de l'utilisateur leur score de départ
        for name, score in user_interests_dict.items():
            if name in by_name:
                result_scores[name] = score

        # =========================================================================
        # ÉTAPE 2 : Propagation des bonus (Descendante et Latérale)
        # =========================================================================
        # On boucle sur chaque intérêt explicite de l'utilisateur pour diffuser son influence
        for name, score in user_interests_dict.items():
            # Si l'intérêt n'est pas présent dans le secteur actuel du contact, on l'ignore
            if name not in by_name:
                continue
                
            node = by_name[name]  # Récupération de l'objet Interest correspondant
            node_id = node.id
            parent_id = node.parent

            # ---------------------------------------------------------------------
            # ENFANTS : Le parent transmet 50% de sa force, bridé à 0.2 maximum
            # ---------------------------------------------------------------------
            for c in children.get(node_id, []):
                c_name = c.name
                
                # Calcul du bonus théorique (50%) et application du plafond strict à 0.2
                bonus_parent = min(score * 0.5, 0.2)
                
                # Cumul : On ajoute ce bonus au score existant de l'enfant (0.0 par défaut)
                result_scores[c_name] = result_scores.get(c_name, 0.0) + bonus_parent

            # ---------------------------------------------------------------------
            # FRÈRES (Siblings) : Un intérêt transmet 20% de sa force à ses frères, bridé à 0.1 maximum
            # ---------------------------------------------------------------------
            if parent_id is not None:
                # On récupère tous les enfants du même parent (la fratrie)
                for s in children.get(parent_id, []):
                    # On évite d'appliquer le bonus à soi-même !
                    if s.id != node_id:
                        s_name = s.name
                        
                        # Calcul du bonus théorique (20%) et application du plafond strict à 0.1
                        bonus_sibling = min(score * 0.2, 0.1)
                        
                        # Cumul : On ajoute ce bonus au score existant du frère (0.0 par défaut)
                        result_scores[s_name] = result_scores.get(s_name, 0.0) + bonus_sibling


        print(f'RESULT SCORES : {result_scores}')    
        # =========================================================================
        # ÉTAPE 3 : Sécurité et Bridage final
        # =========================================================================
        # Aucun intérêt ne doit dépasser la note maximale absolue de 1.0 (100% d'adéquation)
        for name in result_scores:
            result_scores[name] = min(result_scores[name], 1.0)

        # =========================================================================
        # ÉTAPE 4 : Tri et Priorisation
        # =========================================================================
        # 1. On crée un ensemble (set) avec les noms des roots pour un filtrage ultra-rapide (O(1))
        root_names = {r.name for r in roots}

        # 2. On récupère UNIQUEMENT les objets Interest qui ne sont PAS des roots
        matched_interest_objects = [
            by_name[name] for name in result_scores.keys() 
            if name not in root_names
        ]

        # 3. On  renvoie ces objets triés selon le score de leur nom (décroissant), puis par nom (alphabétique)
        #   Le signe '-' devant 'result_scores[x]' force un tri DESCROISSANT sur le score (plus grand en premier).
        #   En deuxième paramètre effectue un tri ALPHABÉTIQUE standard en cas d'égalité parfaite des scores.
        # et les roots
        return sorted(
                matched_interest_objects, 
                key=lambda interest: (-result_scores[interest.name], interest.name)
                ), roots
