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
public class CodeImport  {

    private String type;
    private String alias;
    private String name;

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

    public CodeImport type(String type) {
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

    public CodeImport alias(String alias) {
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

    public CodeImport name(String name) {
        this.name = name;
        return this;
    }

    /**
     * Create a string representation of this pojo.
     **/
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("class CodeImport {\n");

        sb.append("    type: ").append(toIndentedString(type)).append("\n");
        sb.append("    alias: ").append(toIndentedString(alias)).append("\n");
        sb.append("    name: ").append(toIndentedString(name)).append("\n");
        
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
    public static class CodeImportQueryParam  {

        @jakarta.ws.rs.QueryParam("type")
        private String type;
        @jakarta.ws.rs.QueryParam("alias")
        private String alias;
        @jakarta.ws.rs.QueryParam("name")
        private String name;

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

        public CodeImportQueryParam type(String type) {
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

        public CodeImportQueryParam alias(String alias) {
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

        public CodeImportQueryParam name(String name) {
            this.name = name;
            return this;
        }

        /**
         * Create a string representation of this pojo.
         **/
        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("class CodeImportQueryParam {\n");

            sb.append("    type: ").append(toIndentedString(type)).append("\n");
            sb.append("    alias: ").append(toIndentedString(alias)).append("\n");
            sb.append("    name: ").append(toIndentedString(name)).append("\n");
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