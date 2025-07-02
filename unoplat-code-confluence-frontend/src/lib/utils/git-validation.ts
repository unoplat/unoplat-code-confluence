/**
 * Git Repository Validation Utility
 * 
 * Pure utility functions for validating Git repositories that work with both
 * File System Access API (modern browsers) and webkitdirectory fallback (older browsers).
 * 
 * These functions are completely independent of React state or components.
 */

/**
 * Type representing directory input - either a FileSystemDirectoryHandle or FileList
 */
export type DirectoryInput = FileSystemDirectoryHandle | FileList;

/**
 * Validate a Git repository using FileList (webkitdirectory fallback)
 * 
 * @param files - FileList from input[webkitdirectory] selection
 * @returns boolean - true if valid Git repository, false otherwise
 */
function validateGitRepositoryFiles(files: FileList): boolean {
  console.log("[Git Validation] validateGitRepositoryFiles called – total files:", files.length);

  // Convert FileList to an array and stop as soon as we see a "/.git/" segment.
  const hasGitDir = Array.from(files).some((file) =>
    file.webkitRelativePath.includes("/.git/")
  );

  if (hasGitDir) {
    console.log("[Git Validation] Found .git directory – validation passed");
    return true;
  }

  console.log("[Git Validation] No .git directory found in any file paths – validation failed");
  return false;
}

// File System Access API support removed for now – product targets `webkitdirectory` only.
// If/when needed, restore the async `validateGitRepositoryHandle` helper and
// an async `validateGitRepository` wrapper similar to earlier revisions.

// ---------------------------------------------------------------------------
// Public API (synchronous) ---------------------------------------------------
// ---------------------------------------------------------------------------

// Re-export the sync validator under both names for backward compatibility.
// `validateGitRepositorySync` is the preferred import name going forward.

export { validateGitRepositorySync as validateGitRepository };

/**
 * Check if browser supports File System Access API
 * 
 * @returns boolean - true if File System Access API is supported
 */
export function supportsFileSystemAccess(): boolean {
  const supported = 'showDirectoryPicker' in window;
  console.log("[Git Validation] File System Access API supported:", supported);
  return supported;
}

/**
 * Synchronous version of validateGitRepository for immediate validation
 * Only works with FileList (webkitdirectory) - does not support FileSystemDirectoryHandle
 * 
 * @param input - DirectoryInput (FileList only for sync operation)
 * @returns boolean - true if valid Git repository, false otherwise
 */
export function validateGitRepositorySync(input: DirectoryInput): boolean {
  console.log("[Git Validation] validateGitRepositorySync called with input:", input);
  console.log("[Git Validation] Input type:", input?.constructor.name);
  
  try {
    // Handle empty/invalid input
    if (!input) {
      console.log("[Git Validation] Input is null/undefined, returning false");
      return false;
    }

    if (input instanceof FileList) {
      console.log("[Git Validation] Input is FileList, using synchronous webkitdirectory validation");
      
      // Fallback: webkitdirectory file list validation
      if (input.length === 0) {
        console.log("[Git Validation] FileList is empty, returning false");
        return false;
      }

      const result = validateGitRepositoryFiles(input);
      console.log("[Git Validation] Sync FileList validation result:", result);
      return result;
    } else {
      console.log("[Git Validation] FileSystemDirectoryHandle not supported in sync mode, returning false");
      return false;
    }
  } catch (error) {
    console.error("[Git Validation] Error in sync validation:", error);
    return false;
  }
} 