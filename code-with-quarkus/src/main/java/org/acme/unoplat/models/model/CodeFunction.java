package org.acme.unoplat.models.model;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonTypeName;
import com.fasterxml.jackson.annotation.JsonValue;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.lang.reflect.Type;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public class CodeFunction  {

    private String type;
    private String name;
    private String declaration;
    private String description;
    private String syntaxTree;
    private Integer id;
    private String access;
    private List<String> modifiers;
    private String annotation;
    private String frameworkProps;
    private String frameworkFuncs;

    /**
    * Get type
    * @return type
    **/
    @JsonProperty("type")
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

    public CodeFunction type(String type) {
        this.type = type;
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

    public CodeFunction name(String name) {
        this.name = name;
        return this;
    }

    /**
    * Get declaration
    * @return declaration
    **/
    @JsonProperty("Declaration")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getDeclaration() {
        return declaration;
    }

    /**
     * Set declaration
     **/
    public void setDeclaration(String declaration) {
        this.declaration = declaration;
    }

    public CodeFunction declaration(String declaration) {
        this.declaration = declaration;
        return this;
    }

    /**
    * Get description
    * @return description
    **/
    @JsonProperty("Description")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getDescription() {
        return description;
    }

    /**
     * Set description
     **/
    public void setDescription(String description) {
        this.description = description;
    }

    public CodeFunction description(String description) {
        this.description = description;
        return this;
    }

    /**
    * Get syntaxTree
    * @return syntaxTree
    **/
    @JsonProperty("SyntaxTree")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getSyntaxTree() {
        return syntaxTree;
    }

    /**
     * Set syntaxTree
     **/
    public void setSyntaxTree(String syntaxTree) {
        this.syntaxTree = syntaxTree;
    }

    public CodeFunction syntaxTree(String syntaxTree) {
        this.syntaxTree = syntaxTree;
        return this;
    }

    /**
    * Get id
    * @return id
    **/
    @JsonProperty("id")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public Integer getId() {
        return id;
    }

    /**
     * Set id
     **/
    public void setId(Integer id) {
        this.id = id;
    }

    public CodeFunction id(Integer id) {
        this.id = id;
        return this;
    }

    /**
    * Get access
    * @return access
    **/
    @JsonProperty("Access")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getAccess() {
        return access;
    }

    /**
     * Set access
     **/
    public void setAccess(String access) {
        this.access = access;
    }

    public CodeFunction access(String access) {
        this.access = access;
        return this;
    }

    /**
    * Get modifiers
    * @return modifiers
    **/
    @JsonProperty("Modifiers")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<String> getModifiers() {
        return modifiers;
    }

    /**
     * Set modifiers
     **/
    public void setModifiers(List<String> modifiers) {
        this.modifiers = modifiers;
    }

    public CodeFunction modifiers(List<String> modifiers) {
        this.modifiers = modifiers;
        return this;
    }
    public CodeFunction addModifiersItem(String modifiersItem) {
        if (this.modifiers == null){
            modifiers = new ArrayList<>();
        }
        this.modifiers.add(modifiersItem);
        return this;
    }

    /**
    * Get annotation
    * @return annotation
    **/
    @JsonProperty("Annotation")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getAnnotation() {
        return annotation;
    }

    /**
     * Set annotation
     **/
    public void setAnnotation(String annotation) {
        this.annotation = annotation;
    }

    public CodeFunction annotation(String annotation) {
        this.annotation = annotation;
        return this;
    }

    /**
    * Get frameworkProps
    * @return frameworkProps
    **/
    @JsonProperty("FrameworkProps")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getFrameworkProps() {
        return frameworkProps;
    }

    /**
     * Set frameworkProps
     **/
    public void setFrameworkProps(String frameworkProps) {
        this.frameworkProps = frameworkProps;
    }

    public CodeFunction frameworkProps(String frameworkProps) {
        this.frameworkProps = frameworkProps;
        return this;
    }

    /**
    * Get frameworkFuncs
    * @return frameworkFuncs
    **/
    @JsonProperty("FrameworkFuncs")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getFrameworkFuncs() {
        return frameworkFuncs;
    }

    /**
     * Set frameworkFuncs
     **/
    public void setFrameworkFuncs(String frameworkFuncs) {
        this.frameworkFuncs = frameworkFuncs;
    }

    public CodeFunction frameworkFuncs(String frameworkFuncs) {
        this.frameworkFuncs = frameworkFuncs;
        return this;
    }

    /**
     * Create a string representation of this pojo.
     **/
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("class CodeFunction {\n");

        sb.append("    type: ").append(toIndentedString(type)).append("\n");
        sb.append("    name: ").append(toIndentedString(name)).append("\n");
        sb.append("    declaration: ").append(toIndentedString(declaration)).append("\n");
        sb.append("    description: ").append(toIndentedString(description)).append("\n");
        sb.append("    syntaxTree: ").append(toIndentedString(syntaxTree)).append("\n");
        sb.append("    id: ").append(toIndentedString(id)).append("\n");
        sb.append("    access: ").append(toIndentedString(access)).append("\n");
        sb.append("    modifiers: ").append(toIndentedString(modifiers)).append("\n");
        sb.append("    annotation: ").append(toIndentedString(annotation)).append("\n");
        sb.append("    frameworkProps: ").append(toIndentedString(frameworkProps)).append("\n");
        sb.append("    frameworkFuncs: ").append(toIndentedString(frameworkFuncs)).append("\n");
        
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
    public static class CodeFunctionQueryParam  {

        @jakarta.ws.rs.QueryParam("type")
        private String type;
        @jakarta.ws.rs.QueryParam("name")
        private String name;
        @jakarta.ws.rs.QueryParam("declaration")
        private String declaration;
        @jakarta.ws.rs.QueryParam("description")
        private String description;
        @jakarta.ws.rs.QueryParam("syntaxTree")
        private String syntaxTree;
        @jakarta.ws.rs.QueryParam("id")
        private Integer id;
        @jakarta.ws.rs.QueryParam("access")
        private String access;
        @jakarta.ws.rs.QueryParam("modifiers")
        private List<String> modifiers = null;
        @jakarta.ws.rs.QueryParam("annotation")
        private String annotation;
        @jakarta.ws.rs.QueryParam("frameworkProps")
        private String frameworkProps;
        @jakarta.ws.rs.QueryParam("frameworkFuncs")
        private String frameworkFuncs;

        /**
        * Get type
        * @return type
        **/
        @JsonProperty("type")
        public String getType() {
            return type;
        }

        /**
         * Set type
         **/
        public void setType(String type) {
            this.type = type;
        }

        public CodeFunctionQueryParam type(String type) {
            this.type = type;
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

        public CodeFunctionQueryParam name(String name) {
            this.name = name;
            return this;
        }

        /**
        * Get declaration
        * @return declaration
        **/
        @JsonProperty("Declaration")
        public String getDeclaration() {
            return declaration;
        }

        /**
         * Set declaration
         **/
        public void setDeclaration(String declaration) {
            this.declaration = declaration;
        }

        public CodeFunctionQueryParam declaration(String declaration) {
            this.declaration = declaration;
            return this;
        }

        /**
        * Get description
        * @return description
        **/
        @JsonProperty("Description")
        public String getDescription() {
            return description;
        }

        /**
         * Set description
         **/
        public void setDescription(String description) {
            this.description = description;
        }

        public CodeFunctionQueryParam description(String description) {
            this.description = description;
            return this;
        }

        /**
        * Get syntaxTree
        * @return syntaxTree
        **/
        @JsonProperty("SyntaxTree")
        public String getSyntaxTree() {
            return syntaxTree;
        }

        /**
         * Set syntaxTree
         **/
        public void setSyntaxTree(String syntaxTree) {
            this.syntaxTree = syntaxTree;
        }

        public CodeFunctionQueryParam syntaxTree(String syntaxTree) {
            this.syntaxTree = syntaxTree;
            return this;
        }

        /**
        * Get id
        * @return id
        **/
        @JsonProperty("id")
        public Integer getId() {
            return id;
        }

        /**
         * Set id
         **/
        public void setId(Integer id) {
            this.id = id;
        }

        public CodeFunctionQueryParam id(Integer id) {
            this.id = id;
            return this;
        }

        /**
        * Get access
        * @return access
        **/
        @JsonProperty("Access")
        public String getAccess() {
            return access;
        }

        /**
         * Set access
         **/
        public void setAccess(String access) {
            this.access = access;
        }

        public CodeFunctionQueryParam access(String access) {
            this.access = access;
            return this;
        }

        /**
        * Get modifiers
        * @return modifiers
        **/
        @JsonProperty("Modifiers")
        public List<String> getModifiers() {
            return modifiers;
        }

        /**
         * Set modifiers
         **/
        public void setModifiers(List<String> modifiers) {
            this.modifiers = modifiers;
        }

        public CodeFunctionQueryParam modifiers(List<String> modifiers) {
            this.modifiers = modifiers;
            return this;
        }
        public CodeFunctionQueryParam addModifiersItem(String modifiersItem) {
            this.modifiers.add(modifiersItem);
            return this;
        }

        /**
        * Get annotation
        * @return annotation
        **/
        @JsonProperty("Annotation")
        public String getAnnotation() {
            return annotation;
        }

        /**
         * Set annotation
         **/
        public void setAnnotation(String annotation) {
            this.annotation = annotation;
        }

        public CodeFunctionQueryParam annotation(String annotation) {
            this.annotation = annotation;
            return this;
        }

        /**
        * Get frameworkProps
        * @return frameworkProps
        **/
        @JsonProperty("FrameworkProps")
        public String getFrameworkProps() {
            return frameworkProps;
        }

        /**
         * Set frameworkProps
         **/
        public void setFrameworkProps(String frameworkProps) {
            this.frameworkProps = frameworkProps;
        }

        public CodeFunctionQueryParam frameworkProps(String frameworkProps) {
            this.frameworkProps = frameworkProps;
            return this;
        }

        /**
        * Get frameworkFuncs
        * @return frameworkFuncs
        **/
        @JsonProperty("FrameworkFuncs")
        public String getFrameworkFuncs() {
            return frameworkFuncs;
        }

        /**
         * Set frameworkFuncs
         **/
        public void setFrameworkFuncs(String frameworkFuncs) {
            this.frameworkFuncs = frameworkFuncs;
        }

        public CodeFunctionQueryParam frameworkFuncs(String frameworkFuncs) {
            this.frameworkFuncs = frameworkFuncs;
            return this;
        }

        /**
         * Create a string representation of this pojo.
         **/
        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("class CodeFunctionQueryParam {\n");

            sb.append("    type: ").append(toIndentedString(type)).append("\n");
            sb.append("    name: ").append(toIndentedString(name)).append("\n");
            sb.append("    declaration: ").append(toIndentedString(declaration)).append("\n");
            sb.append("    description: ").append(toIndentedString(description)).append("\n");
            sb.append("    syntaxTree: ").append(toIndentedString(syntaxTree)).append("\n");
            sb.append("    id: ").append(toIndentedString(id)).append("\n");
            sb.append("    access: ").append(toIndentedString(access)).append("\n");
            sb.append("    modifiers: ").append(toIndentedString(modifiers)).append("\n");
            sb.append("    annotation: ").append(toIndentedString(annotation)).append("\n");
            sb.append("    frameworkProps: ").append(toIndentedString(frameworkProps)).append("\n");
            sb.append("    frameworkFuncs: ").append(toIndentedString(frameworkFuncs)).append("\n");
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