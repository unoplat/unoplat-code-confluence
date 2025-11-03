declare module 'eslint-plugin-use-no-memo' {
  import type { ESLint, Linter } from 'eslint';

  interface UseNoMemoPlugin extends ESLint.Plugin {
    rules: {
      'react-hook-form': Linter.RuleEntry;
      'tanstack-table': Linter.RuleEntry;
    };
  }

  const plugin: UseNoMemoPlugin;
  export default plugin;
}
