# Business Logic References

## Domain Summary
The codebase primarily models a documentation site for Unoplat Code Confluence, centered on release communications and page metadata such as banner announcements, changelog entries, SEO/canonical tags, and TanStack route structure for docs, changelog, and search pages. It also includes a reusable data-table filtering domain for typed column configs, operators, and faceted filtering across text, number, date, and option-based columns.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/filters.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/filters.ts#L161-L167` — `FluentColumnConfigHelper`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L22-L29` — `ColumnOption`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L31-L34` — `ColumnOptionExtended`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L39-L47` — `ColumnDataType`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L52-L55` — `OptionBasedColumnDataType`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L60-L66` — `ColumnDataNativeMap`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L72-L74` — `FilterValues`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L86-L88` — `TTransformOptionFn`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L94-L97` — `TOrderFn`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L102-L123` — `ColumnConfig`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L125-L132` — `OptionColumnId`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L134-L138` — `OptionColumnIds`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L140-L147` — `NumberColumnId`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L149-L153` — `NumberColumnIds`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L158-L167` — `ColumnConfigHelper`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L169-L172` — `DataTableFilterConfig`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L174-L183` — `ColumnProperties`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L185-L190` — `ColumnPrivateProperties`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L192-L198` — `Column`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L204-L228` — `DataTableFilterActions`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L236-L244` — `NumberFilterOperator`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L247-L255` — `DateFilterOperator`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L261-L267` — `MultiOptionFilterOperator`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L270-L276` — `FilterOperators`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L287-L292` — `FilterModel`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L299-L301` — `FilterDetails`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L305-L327` — `FilterOperatorDetailsBase`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L335-L347` — `FilterOperatorDetails`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/core/types.ts#L350-L352` — `FilterTypeOperatorDetails`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/lib/debounce.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/lib/debounce.ts#L1-L5` — `ControlFunctions`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/components/data-table-filter/lib/debounce.ts#L7-L11` — `DebounceOptions`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/lib/banner-config.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/lib/banner-config.ts#L12-L27` — `BannerConfig`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/lib/changelog-utils.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/lib/changelog-utils.ts#L6-L14` — `ChangelogEntry`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/lib/seo.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/lib/seo.ts#L12-L17` — `SeoOptions`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/routeTree.gen.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/routeTree.gen.ts#L44-L50` — `FileRoutesByFullPath`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/routeTree.gen.ts#L51-L57` — `FileRoutesByTo`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/routeTree.gen.ts#L58-L65` — `FileRoutesById`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/routeTree.gen.ts#L66-L84` — `FileRouteTypes`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/routeTree.gen.ts#L85-L91` — `RootRouteChildren`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/routeTree.gen.ts#L94-L130` — `FileRoutesByPath`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/routeTree.gen.ts#L147-L150` — `Register`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/types/framework-catalog.ts`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-docs/src/types/framework-catalog.ts#L1-L7` — `FrameworkCatalogRow`
