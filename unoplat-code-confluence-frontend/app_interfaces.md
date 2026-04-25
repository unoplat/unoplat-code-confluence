# App Interfaces

Format: `path: L<line>: <match_text>` where path is codebase-relative.

## Inbound Constructs

No inbound constructs detected.

## Outbound Constructs

No outbound constructs detected.

## Internal Constructs

### key_value_store.store_definition (zustand)

- `src/features/agent-feedback/store.ts`: L59: create<AgentFeedbackState>()
- `src/features/app-feedback/store.ts`: L10: create<AppFeedbackSheetState>()
- `src/stores/useAuthStore.ts`: L11: create<AuthState>()
- `src/stores/useCommandPaletteStore.ts`: L10: create<CommandPaletteState>()
- `src/stores/useDevModeStore.ts`: L9: create<DevModeState>()( persist( (set) => ({ isDevMode: false, setDevMode: (value: boolean) => set({ isDevMode: value }), }), { name: "dev-mode-storage", storage: createJSONStorage(() => localStorage), partialize: (state) => ({ isDevMode: state.isDevMode }), }, ), )
- `src/stores/useThemeStore.ts`: L11: create<ThemeState>()
