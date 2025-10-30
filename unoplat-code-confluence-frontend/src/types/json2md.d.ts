declare module "json2md" {
  export interface Json2MdHeading1 {
    h1: string;
  }
  export interface Json2MdHeading2 {
    h2: string;
  }
  export interface Json2MdHeading3 {
    h3: string;
  }
  export interface Json2MdParagraph {
    p: string | string[];
  }
  export interface Json2MdUl {
    ul: Array<string>;
  }
  export interface Json2MdOl {
    ol: Array<string>;
  }
  export interface Json2MdCode {
    code: { language?: string; content: string | string[] };
  }
  export interface Json2MdTable {
    table: { headers: string[]; rows: Array<Array<string | number>> };
  }

  export type Json2MdInput =
    | Json2MdHeading1
    | Json2MdHeading2
    | Json2MdHeading3
    | Json2MdParagraph
    | Json2MdUl
    | Json2MdOl
    | Json2MdCode
    | Json2MdTable;

  declare function json2md(input: Json2MdInput | Json2MdInput[]): string;
  export default json2md;
}
