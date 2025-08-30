"""Service for managing feature flags using the existing commons Flag model."""

from typing import List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from unoplat_code_confluence_commons.flags import Flag

from unoplat_code_confluence_query_engine.db.postgres.db import get_session


class FlagService:
    """Service for managing feature flags using the shared Flag model from commons."""
    
    async def get_flag(self, flag_name: str) -> Optional[Flag]:
        """Get a specific flag by name.
        
        Args:
            flag_name: The name of the flag to retrieve
            
        Returns:
            Flag if found, None otherwise
        """
        try:
            async with get_session() as session:
                result = await session.execute(select(Flag).where(Flag.name == flag_name))
                return result.scalar_one_or_none()
                
        except SQLAlchemyError as e:
            logger.error("Database error getting flag {}: {}", flag_name, e)
            raise
        except Exception as e:
            logger.error("Unexpected error getting flag {}: {}", flag_name, e)
            raise
    
    async def get_flag_status(self, flag_name: str) -> Optional[bool]:
        """Get the status of a specific flag by name.
        
        Args:
            flag_name: The name of the flag to check
            
        Returns:
            Flag status (True/False) if found, None if flag doesn't exist
        """
        flag = await self.get_flag(flag_name)
        return flag.status if flag else None
    
    async def list_all_flags(self) -> List[Flag]:
        """Get all feature flags.
        
        Returns:
            List of all flags
        """
        try:
            async with get_session() as session:
                result = await session.execute(select(Flag))
                return list(result.scalars().all())
                
        except SQLAlchemyError as e:
            logger.error("Database error listing flags: {}", e)
            raise
        except Exception as e:
            logger.error("Unexpected error listing flags: {}", e)
            raise
    
    async def upsert_flag(self, flag_name: str, status: bool) -> Flag:
        """Create or update a flag with the given status.
        
        Args:
            flag_name: The name of the flag
            status: The status to set
            
        Returns:
            The created or updated Flag
        """
        try:
            async with get_session() as session:
                result = await session.execute(select(Flag).where(Flag.name == flag_name))
                flag = result.scalar_one_or_none()
                
                if flag:
                    # Update existing flag
                    flag.status = status
                    logger.info("Updated flag {}: status={}", flag_name, status)
                else:
                    # Create new flag
                    flag = Flag(name=flag_name, status=status)
                    session.add(flag)
                    logger.info("Created flag {}: status={}", flag_name, status)
                
                # Context manager handles commit/rollback automatically
                return flag
                
        except SQLAlchemyError as e:
            logger.error("Database error upserting flag {} with status {}: {}", flag_name, status, e)
            raise
        except Exception as e:
            logger.error("Unexpected error upserting flag {} with status {}: {}", flag_name, status, e)
            raise
    
    async def delete_flag(self, flag_name: str) -> bool:
        """Delete a flag by name.
        
        Args:
            flag_name: The name of the flag to delete
            
        Returns:
            True if flag was deleted, False if flag didn't exist
        """
        try:
            async with get_session() as session:
                result = await session.execute(select(Flag).where(Flag.name == flag_name))
                flag = result.scalar_one_or_none()
                
                if flag:
                    await session.delete(flag)
                    # Context manager handles commit/rollback automatically
                    logger.info("Deleted flag: {}", flag_name)
                    return True
                else:
                    logger.info("Flag not found for deletion: {}", flag_name)
                    return False
                    
        except SQLAlchemyError as e:
            logger.error("Database error deleting flag {}: {}", flag_name, e)
            raise
        except Exception as e:
            logger.error("Unexpected error deleting flag {}: {}", flag_name, e)
            raise
    
    async def flag_exists(self, flag_name: str) -> bool:
        """Check if a flag exists.
        
        Args:
            flag_name: The name of the flag to check
            
        Returns:
            True if flag exists, False otherwise
        """
        try:
            async with get_session() as session:
                result = await session.execute(select(Flag.id).where(Flag.name == flag_name))
                return result.scalar_one_or_none() is not None
                
        except SQLAlchemyError as e:
            logger.error("Database error checking flag existence {}: {}", flag_name, e)
            raise
        except Exception as e:
            logger.error("Unexpected error checking flag existence {}: {}", flag_name, e)
            raise