from typing import Any, List, Union, Dict

def normalize_authors(authors: Union[List[str], List[Dict[str, Any]], None]) -> List[str]:
    """
    Normalize authors from Poetry (list of strings) or PEP 621/UV (list of dicts) to a list of 'Name <email>' strings.

    Args:
        authors: List of author strings (Poetry) or list of dicts with 'name' and 'email' (PEP 621/UV)

    Returns:
        List[str]: List of authors in 'Name <email>' format
    """
    if not authors:
        return []
    if isinstance(authors, list):
        if all(isinstance(a, str) for a in authors):
            # Poetry format: already list of strings
            return [a for a in authors if isinstance(a, str)]
        elif all(isinstance(a, dict) for a in authors):
            # UV/PEP 621 format: list of dicts
            normalized: List[str] = []
            for author in authors:
                if isinstance(author, dict):
                    name = str(author.get('name', '')).strip()
                    email = str(author.get('email', '')).strip()
                    if name and email:
                        normalized.append(f"{name} <{email}>")
                    elif name:
                        normalized.append(name)
                    elif email:
                        normalized.append(f"<{email}>")
            return normalized
    # Fallback: return empty list if format is unexpected
    return [] 