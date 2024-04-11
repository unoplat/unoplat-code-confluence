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
public class CodePosition  {

    private String filePath;
    private Integer start;
    private Integer end;

    /**
    * Get filePath
    * @return filePath
    **/
    @JsonProperty("FilePath")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getFilePath() {
        return filePath;
    }

    /**
     * Set filePath
     **/
    public void setFilePath(String filePath) {
        this.filePath = filePath;
    }

    public CodePosition filePath(String filePath) {
        this.filePath = filePath;
        return this;
    }

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

    public CodePosition start(Integer start) {
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

    public CodePosition end(Integer end) {
        this.end = end;
        return this;
    }

    /**
     * Create a string representation of this pojo.
     **/
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("class CodePosition {\n");

        sb.append("    filePath: ").append(toIndentedString(filePath)).append("\n");
        sb.append("    start: ").append(toIndentedString(start)).append("\n");
        sb.append("    end: ").append(toIndentedString(end)).append("\n");
        
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
    public static class CodePositionQueryParam  {

        @jakarta.ws.rs.QueryParam("filePath")
        private String filePath;
        @jakarta.ws.rs.QueryParam("start")
        private Integer start;
        @jakarta.ws.rs.QueryParam("end")
        private Integer end;

        /**
        * Get filePath
        * @return filePath
        **/
        @JsonProperty("FilePath")
        public String getFilePath() {
            return filePath;
        }

        /**
         * Set filePath
         **/
        public void setFilePath(String filePath) {
            this.filePath = filePath;
        }

        public CodePositionQueryParam filePath(String filePath) {
            this.filePath = filePath;
            return this;
        }

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

        public CodePositionQueryParam start(Integer start) {
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

        public CodePositionQueryParam end(Integer end) {
            this.end = end;
            return this;
        }

        /**
         * Create a string representation of this pojo.
         **/
        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("class CodePositionQueryParam {\n");

            sb.append("    filePath: ").append(toIndentedString(filePath)).append("\n");
            sb.append("    start: ").append(toIndentedString(start)).append("\n");
            sb.append("    end: ").append(toIndentedString(end)).append("\n");
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