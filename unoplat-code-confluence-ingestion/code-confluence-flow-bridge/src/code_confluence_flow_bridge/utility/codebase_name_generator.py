import re
from typing import Optional


class CodebaseNameGenerator:
    """
    Utility to derive a unique, normalized codebase name from folder/package info.
    """

    @staticmethod
    def slugify(segment: str) -> str:
        """
        Lower‑case the input, replace non‑alphanumerics with underscores,
        collapse multiple underscores, and strip leading/trailing underscores.
        """
        s = segment.lower()
        # replace any group of non-word chars with single underscore
        s = re.sub(r"[^\w]+", "_", s)
        # collapse multiple underscores
        s = re.sub(r"_+", "_", s)
        # strip leading/trailing underscores
        return s.strip("_")

    @classmethod
    def derive_name(
        cls,
        codebase_folder: Optional[str],
        root_package: Optional[str],
        repository_name: str,
    ) -> str:
        """
        Derive a unique codebase name:
         - If codebase_folder != "." and is non-empty, split on "/" and slugify each piece.
         - Else if root_package != "." and non-empty, split on "/" or "." and slugify each piece.
         - Else fallback to slugified repository_name.
        Joined with "__" to keep segments distinct.
        """
        # Prefer explicit folder path
        if codebase_folder and codebase_folder != ".":
            parts = codebase_folder.split("/")
            slugged = [cls.slugify(p) for p in parts if p and p != "."]
            if slugged:
                return "__".join(slugged)

        # Fallback to package path
        if root_package and root_package != ".":
            parts = re.split(r"[\/\.]", root_package)
            slugged = [cls.slugify(p) for p in parts if p and p != "."]
            if slugged:
                return "__".join(slugged)

        # Final fallback to repo name
        return cls.slugify(repository_name)