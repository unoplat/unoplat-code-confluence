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
public class CodeCall  {

    private Integer start;
    private Integer end;
    private String nameSpace;
    private String name;
    private String type;

    /**
    * Get start
    * @return start
    **/
    @JsonProperty("Start")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public Integer getStart() {
        return start;
    }

    /**
     * Set start
     **/
    public void setStart(Integer start) {
        this.start = start;
    }

    public CodeCall start(Integer start) {
        this.start = start;
        return this;
    }

    /**
    * Get end
    * @return end
    **/
    @JsonProperty("End")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public Integer getEnd() {
        return end;
    }

    /**
     * Set end
     **/
    public void setEnd(Integer end) {
        this.end = end;
    }

    public CodeCall end(Integer end) {
        this.end = end;
        return this;
    }

    /**
    * Get nameSpace
    * @return nameSpace
    **/
    @JsonProperty("NameSpace")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getNameSpace() {
        return nameSpace;
    }

    /**
     * Set nameSpace
     **/
    public void setNameSpace(String nameSpace) {
        this.nameSpace = nameSpace;
    }

    public CodeCall nameSpace(String nameSpace) {
        this.nameSpace = nameSpace;
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

    public CodeCall name(String name) {
        this.name = name;
        return this;
    }

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

    public CodeCall type(String type) {
        this.type = type;
        return this;
    }

    /**
     * Create a string representation of this pojo.
     **/
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("class CodeCall {\n");

        sb.append("    start: ").append(toIndentedString(start)).append("\n");
        sb.append("    end: ").append(toIndentedString(end)).append("\n");
        sb.append("    nameSpace: ").append(toIndentedString(nameSpace)).append("\n");
        sb.append("    name: ").append(toIndentedString(name)).append("\n");
        sb.append("    type: ").append(toIndentedString(type)).append("\n");
        
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
    public static class CodeCallQueryParam  {

        @jakarta.ws.rs.QueryParam("start")
        private Integer start;
        @jakarta.ws.rs.QueryParam("end")
        private Integer end;
        @jakarta.ws.rs.QueryParam("nameSpace")
        private String nameSpace;
        @jakarta.ws.rs.QueryParam("name")
        private String name;
        @jakarta.ws.rs.QueryParam("type")
        private String type;

        /**
        * Get start
        * @return start
        **/
        @JsonProperty("Start")
        public Integer getStart() {
            return start;
        }

        /**
         * Set start
         **/
        public void setStart(Integer start) {
            this.start = start;
        }

        public CodeCallQueryParam start(Integer start) {
            this.start = start;
            return this;
        }

        /**
        * Get end
        * @return end
        **/
        @JsonProperty("End")
        public Integer getEnd() {
            return end;
        }

        /**
         * Set end
         **/
        public void setEnd(Integer end) {
            this.end = end;
        }

        public CodeCallQueryParam end(Integer end) {
            this.end = end;
            return this;
        }

        /**
        * Get nameSpace
        * @return nameSpace
        **/
        @JsonProperty("NameSpace")
        public String getNameSpace() {
            return nameSpace;
        }

        /**
         * Set nameSpace
         **/
        public void setNameSpace(String nameSpace) {
            this.nameSpace = nameSpace;
        }

        public CodeCallQueryParam nameSpace(String nameSpace) {
            this.nameSpace = nameSpace;
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

        public CodeCallQueryParam name(String name) {
            this.name = name;
            return this;
        }

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

        public CodeCallQueryParam type(String type) {
            this.type = type;
            return this;
        }

        /**
         * Create a string representation of this pojo.
         **/
        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("class CodeCallQueryParam {\n");

            sb.append("    start: ").append(toIndentedString(start)).append("\n");
            sb.append("    end: ").append(toIndentedString(end)).append("\n");
            sb.append("    nameSpace: ").append(toIndentedString(nameSpace)).append("\n");
            sb.append("    name: ").append(toIndentedString(name)).append("\n");
            sb.append("    type: ").append(toIndentedString(type)).append("\n");
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