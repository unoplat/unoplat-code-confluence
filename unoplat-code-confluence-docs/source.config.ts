import {
  defineConfig,
  defineDocs,
  defineCollections,
  frontmatterSchema,
} from "fumadocs-mdx/config";

const baseString = frontmatterSchema.shape.title;

export const docs = defineDocs({
  dir: "content/docs",
});

export const changelog = defineCollections({
  type: "doc",
  dir: "content/changelog",
  schema: frontmatterSchema.extend({
    version: baseString,
    releaseDate: baseString,
    githubRelease: baseString.optional(),
  }),
});

export default defineConfig();
