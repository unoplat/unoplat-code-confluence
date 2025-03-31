import { useState } from 'react';
import React from 'react';

interface GitHubAuthProps {
  onAuthenticate: (token: string) => void;
  onSkip: () => void;
}

export function GitHubAuth({ onAuthenticate, onSkip }: GitHubAuthProps): React.ReactElement {
  const [patToken, setPatToken] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    if (!patToken.trim()) return;
    
    setIsSubmitting(true);
    try {
      // In a real implementation, we would validate the token here
      // For now, we'll just simulate a successful authentication
      await new Promise((resolve) => setTimeout(resolve, 1000));
      onAuthenticate(patToken.trim());
    } catch (error) {
      console.error('Authentication error:', error);
      // Handle error
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          GitHub Repository Access
        </h3>
        <div className="mt-2 max-w-xl text-sm text-gray-500">
          <p>
            Provide a GitHub Personal Access Token (PAT) to access both public and private repositories. 
            Skip this step to access only public repositories.
          </p>
        </div>
        <form className="mt-5 sm:flex sm:items-center" onSubmit={handleSubmit}>
          <div className="w-full sm:max-w-xs">
            <label htmlFor="pat-token" className="sr-only">
              GitHub PAT Token
            </label>
            <input
              type="text"
              name="pat-token"
              id="pat-token"
              className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
              placeholder="Enter your PAT token"
              value={patToken}
              onChange={(e) => setPatToken(e.target.value)}
              disabled={isSubmitting}
            />
          </div>
          <div className="mt-3 sm:mt-0 sm:ml-4 sm:flex-shrink-0 flex space-x-3">
            <button
              type="submit"
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
                isSubmitting ? 'opacity-75 cursor-not-allowed' : ''
              }`}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Authenticating...' : 'Authenticate'}
            </button>
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              onClick={onSkip}
              disabled={isSubmitting}
            >
              Skip
            </button>
          </div>
        </form>
        <div className="mt-4 text-sm text-gray-500">
          <p>
            Note: To create a PAT token, go to GitHub &rarr; Settings &rarr; Developer settings &rarr; Personal access tokens.
          </p>
        </div>
      </div>
    </div>
  );
} 