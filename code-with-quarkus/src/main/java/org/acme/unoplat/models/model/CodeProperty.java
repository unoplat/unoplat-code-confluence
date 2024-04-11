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
public class CodeProperty  {

    private String typeType;
    private String typeValue;
    private String typeKey;
    private List<String> modifiers;
    private List<CodeAnnotation> annotations;
    private String name;
    private String value;

    /**
    * Get typeType
    * @return typeType
    **/
    @JsonProperty("TypeType")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getTypeType() {
        return typeType;
    }

    /**
     * Set typeType
     **/
    public void setTypeType(String typeType) {
        this.typeType = typeType;
    }

    public CodeProperty typeType(String typeType) {
        this.typeType = typeType;
        return this;
    }

    /**
    * Get typeValue
    * @return typeValue
    **/
    @JsonProperty("TypeValue")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getTypeValue() {
        return typeValue;
    }

    /**
     * Set typeValue
     **/
    public void setTypeValue(String typeValue) {
        this.typeValue = typeValue;
    }

    public CodeProperty typeValue(String typeValue) {
        this.typeValue = typeValue;
        return this;
    }

    /**
    * Get typeKey
    * @return typeKey
    **/
    @JsonProperty("TypeKey")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getTypeKey() {
        return typeKey;
    }

    /**
     * Set typeKey
     **/
    public void setTypeKey(String typeKey) {
        this.typeKey = typeKey;
    }

    public CodeProperty typeKey(String typeKey) {
        this.typeKey = typeKey;
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

    public CodeProperty modifiers(List<String> modifiers) {
        this.modifiers = modifiers;
        return this;
    }
    public CodeProperty addModifiersItem(String modifiersItem) {
        if (this.modifiers == null){
            modifiers = new ArrayList<>();
        }
        this.modifiers.add(modifiersItem);
        return this;
    }

    /**
    * Get annotations
    * @return annotations
    **/
    @JsonProperty("Annotations")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<CodeAnnotation> getAnnotations() {
        return annotations;
    }

    /**
     * Set annotations
     **/
    public void setAnnotations(List<CodeAnnotation> annotations) {
        this.annotations = annotations;
    }

    public CodeProperty annotations(List<CodeAnnotation> annotations) {
        this.annotations = annotations;
        return this;
    }
    public CodeProperty addAnnotationsItem(CodeAnnotation annotationsItem) {
        if (this.annotations == null){
            annotations = new ArrayList<>();
        }
        this.annotations.add(annotationsItem);
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

    public CodeProperty name(String name) {
        this.name = name;
        return this;
    }

    /**
    * Get value
    * @return value
    **/
    @JsonProperty("Value")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getValue() {
        return value;
    }

    /**
     * Set value
     **/
    public void setValue(String value) {
        this.value = value;
    }

    public CodeProperty value(String value) {
        this.value = value;
        return this;
    }

    /**
     * Create a string representation of this pojo.
     **/
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("class CodeProperty {\n");

        sb.append("    typeType: ").append(toIndentedString(typeType)).append("\n");
        sb.append("    typeValue: ").append(toIndentedString(typeValue)).append("\n");
        sb.append("    typeKey: ").append(toIndentedString(typeKey)).append("\n");
        sb.append("    modifiers: ").append(toIndentedString(modifiers)).append("\n");
        sb.append("    annotations: ").append(toIndentedString(annotations)).append("\n");
        sb.append("    name: ").append(toIndentedString(name)).append("\n");
        sb.append("    value: ").append(toIndentedString(value)).append("\n");
        
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
    public static class CodePropertyQueryParam  {

        @jakarta.ws.rs.QueryParam("typeType")
        private String typeType;
        @jakarta.ws.rs.QueryParam("typeValue")
        private String typeValue;
        @jakarta.ws.rs.QueryParam("typeKey")
        private String typeKey;
        @jakarta.ws.rs.QueryParam("modifiers")
        private List<String> modifiers = null;
        @jakarta.ws.rs.QueryParam("annotations")
        private List<CodeAnnotation> annotations = null;
        @jakarta.ws.rs.QueryParam("name")
        private String name;
        @jakarta.ws.rs.QueryParam("value")
        private String value;

        /**
        * Get typeType
        * @return typeType
        **/
        @JsonProperty("TypeType")
        public String getTypeType() {
            return typeType;
        }

        /**
         * Set typeType
         **/
        public void setTypeType(String typeType) {
            this.typeType = typeType;
        }

        public CodePropertyQueryParam typeType(String typeType) {
            this.typeType = typeType;
            return this;
        }

        /**
        * Get typeValue
        * @return typeValue
        **/
        @JsonProperty("TypeValue")
        public String getTypeValue() {
            return typeValue;
        }

        /**
         * Set typeValue
         **/
        public void setTypeValue(String typeValue) {
            this.typeValue = typeValue;
        }

        public CodePropertyQueryParam typeValue(String typeValue) {
            this.typeValue = typeValue;
            return this;
        }

        /**
        * Get typeKey
        * @return typeKey
        **/
        @JsonProperty("TypeKey")
        public String getTypeKey() {
            return typeKey;
        }

        /**
         * Set typeKey
         **/
        public void setTypeKey(String typeKey) {
            this.typeKey = typeKey;
        }

        public CodePropertyQueryParam typeKey(String typeKey) {
            this.typeKey = typeKey;
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

        public CodePropertyQueryParam modifiers(List<String> modifiers) {
            this.modifiers = modifiers;
            return this;
        }
        public CodePropertyQueryParam addModifiersItem(String modifiersItem) {
            this.modifiers.add(modifiersItem);
            return this;
        }

        /**
        * Get annotations
        * @return annotations
        **/
        @JsonProperty("Annotations")
        public List<CodeAnnotation> getAnnotations() {
            return annotations;
        }

        /**
         * Set annotations
         **/
        public void setAnnotations(List<CodeAnnotation> annotations) {
            this.annotations = annotations;
        }

        public CodePropertyQueryParam annotations(List<CodeAnnotation> annotations) {
            this.annotations = annotations;
            return this;
        }
        public CodePropertyQueryParam addAnnotationsItem(CodeAnnotation annotationsItem) {
            this.annotations.add(annotationsItem);
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

        public CodePropertyQueryParam name(String name) {
            this.name = name;
            return this;
        }

        /**
        * Get value
        * @return value
        **/
        @JsonProperty("Value")
        public String getValue() {
            return value;
        }

        /**
         * Set value
         **/
        public void setValue(String value) {
            this.value = value;
        }

        public CodePropertyQueryParam value(String value) {
            this.value = value;
            return this;
        }

        /**
         * Create a string representation of this pojo.
         **/
        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("class CodePropertyQueryParam {\n");

            sb.append("    typeType: ").append(toIndentedString(typeType)).append("\n");
            sb.append("    typeValue: ").append(toIndentedString(typeValue)).append("\n");
            sb.append("    typeKey: ").append(toIndentedString(typeKey)).append("\n");
            sb.append("    modifiers: ").append(toIndentedString(modifiers)).append("\n");
            sb.append("    annotations: ").append(toIndentedString(annotations)).append("\n");
            sb.append("    name: ").append(toIndentedString(name)).append("\n");
            sb.append("    value: ").append(toIndentedString(value)).append("\n");
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