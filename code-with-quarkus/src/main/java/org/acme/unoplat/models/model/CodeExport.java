package org.acme.unoplat.models.model;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonTypeName;
import com.fasterxml.jackson.annotation.JsonValue;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.lang.reflect.Type;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class CodeExport  {

    private String type;
    private String alias;
    private String name;
    private String extension;
    private String content;

    /**
    * Get type
    * @return type
    **/
    @JsonProperty("Type")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getType() {
        return type;
    }

    /**
     * Set type
     **/
    public void setType(String type) {
        this.type = type;
    }

    public CodeExport type(String type) {
        this.type = type;
        return this;
    }

    /**
    * Get alias
    * @return alias
    **/
    @JsonProperty("Alias")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getAlias() {
        return alias;
    }

    /**
     * Set alias
     **/
    public void setAlias(String alias) {
        this.alias = alias;
    }

    public CodeExport alias(String alias) {
        this.alias = alias;
        return this;
    }

    /**
    * Get name
    * @return name
    **/
    @JsonProperty("Name")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getName() {
        return name;
    }

    /**
     * Set name
     **/
    public void setName(String name) {
        this.name = name;
    }

    public CodeExport name(String name) {
        this.name = name;
        return this;
    }

    /**
    * Get extension
    * @return extension
    **/
    @JsonProperty("Extension")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getExtension() {
        return extension;
    }

    /**
     * Set extension
     **/
    public void setExtension(String extension) {
        this.extension = extension;
    }

    public CodeExport extension(String extension) {
        this.extension = extension;
        return this;
    }

    /**
    * Get content
    * @return content
    **/
    @JsonProperty("Content")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getContent() {
        return content;
    }

    /**
     * Set content
     **/
    public void setContent(String content) {
        this.content = content;
    }

    public CodeExport content(String content) {
        this.content = content;
        return this;
    }

    /**
     * Create a string representation of this pojo.
     **/
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("class CodeExport {\n");

        sb.append("    type: ").append(toIndentedString(type)).append("\n");
        sb.append("    alias: ").append(toIndentedString(alias)).append("\n");
        sb.append("    name: ").append(toIndentedString(name)).append("\n");
        sb.append("    extension: ").append(toIndentedString(extension)).append("\n");
        sb.append("    content: ").append(toIndentedString(content)).append("\n");
        
        sb.append("}");
        return sb.toString();
    }

    /**
     * Convert the given object to string with each line indented by 4 spaces
     * (except the first line).
     */
    private static String toIndentedString(Object o) {
        if (o == null) {
            return "null";
        }
        return o.toString().replace("\n", "\n    ");
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class CodeExportQueryParam  {

        @jakarta.ws.rs.QueryParam("type")
        private String type;
        @jakarta.ws.rs.QueryParam("alias")
        private String alias;
        @jakarta.ws.rs.QueryParam("name")
        private String name;
        @jakarta.ws.rs.QueryParam("extension")
        private String extension;
        @jakarta.ws.rs.QueryParam("content")
        private String content;

        /**
        * Get type
        * @return type
        **/
        @JsonProperty("Type")
        public String getType() {
            return type;
        }

        /**
         * Set type
         **/
        public void setType(String type) {
            this.type = type;
        }

        public CodeExportQueryParam type(String type) {
            this.type = type;
            return this;
        }

        /**
        * Get alias
        * @return alias
        **/
        @JsonProperty("Alias")
        public String getAlias() {
            return alias;
        }

        /**
         * Set alias
         **/
        public void setAlias(String alias) {
            this.alias = alias;
        }

        public CodeExportQueryParam alias(String alias) {
            this.alias = alias;
            return this;
        }

        /**
        * Get name
        * @return name
        **/
        @JsonProperty("Name")
        public String getName() {
            return name;
        }

        /**
         * Set name
         **/
        public void setName(String name) {
            this.name = name;
        }

        public CodeExportQueryParam name(String name) {
            this.name = name;
            return this;
        }

        /**
        * Get extension
        * @return extension
        **/
        @JsonProperty("Extension")
        public String getExtension() {
            return extension;
        }

        /**
         * Set extension
         **/
        public void setExtension(String extension) {
            this.extension = extension;
        }

        public CodeExportQueryParam extension(String extension) {
            this.extension = extension;
            return this;
        }

        /**
        * Get content
        * @return content
        **/
        @JsonProperty("Content")
        public String getContent() {
            return content;
        }

        /**
         * Set content
         **/
        public void setContent(String content) {
            this.content = content;
        }

        public CodeExportQueryParam content(String content) {
            this.content = content;
            return this;
        }

        /**
         * Create a string representation of this pojo.
         **/
        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("class CodeExportQueryParam {\n");

            sb.append("    type: ").append(toIndentedString(type)).append("\n");
            sb.append("    alias: ").append(toIndentedString(alias)).append("\n");
            sb.append("    name: ").append(toIndentedString(name)).append("\n");
            sb.append("    extension: ").append(toIndentedString(extension)).append("\n");
            sb.append("    content: ").append(toIndentedString(content)).append("\n");
            sb.append("}");
            return sb.toString();
        }

        /**
         * Convert the given object to string with each line indented by 4 spaces
         * (except the first line).
         */
        private static String toIndentedString(Object o) {
            if (o == null) {
                return "null";
            }
            return o.toString().replace("\n", "\n    ");
        }
    }
}