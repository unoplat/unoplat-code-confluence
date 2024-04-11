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
public class CodeDataStruct  {

    private String nodeName;
    private String module;
    private String type;
    private String _package;
    private String filePath;
    private List<CodeField> fields;
    private List<String> multipleExtend;
    private List<String> _implements;
    private String extend;
    private List<CodeFunction> functions;
    private List<CodeDataStruct> innerStructures;
    private List<CodeAnnotation> annotations;
    private List<CodeCall> functionCalls;
    private List<CodeProperty> parameters;
    private List<CodeImport> imports;
    private List<CodeExport> exports;
    private String extension;
    private CodePosition position;
    private String content;

    /**
    * Get nodeName
    * @return nodeName
    **/
    @JsonProperty("NodeName")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getNodeName() {
        return nodeName;
    }

    /**
     * Set nodeName
     **/
    public void setNodeName(String nodeName) {
        this.nodeName = nodeName;
    }

    public CodeDataStruct nodeName(String nodeName) {
        this.nodeName = nodeName;
        return this;
    }

    /**
    * Get module
    * @return module
    **/
    @JsonProperty("Module")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getModule() {
        return module;
    }

    /**
     * Set module
     **/
    public void setModule(String module) {
        this.module = module;
    }

    public CodeDataStruct module(String module) {
        this.module = module;
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

    public CodeDataStruct type(String type) {
        this.type = type;
        return this;
    }

    /**
    * Get _package
    * @return _package
    **/
    @JsonProperty("Package")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getPackage() {
        return _package;
    }

    /**
     * Set _package
     **/
    public void setPackage(String _package) {
        this._package = _package;
    }

    public CodeDataStruct _package(String _package) {
        this._package = _package;
        return this;
    }

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

    public CodeDataStruct filePath(String filePath) {
        this.filePath = filePath;
        return this;
    }

    /**
    * Get fields
    * @return fields
    **/
    @JsonProperty("Fields")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<CodeField> getFields() {
        return fields;
    }

    /**
     * Set fields
     **/
    public void setFields(List<CodeField> fields) {
        this.fields = fields;
    }

    public CodeDataStruct fields(List<CodeField> fields) {
        this.fields = fields;
        return this;
    }
    public CodeDataStruct addFieldsItem(CodeField fieldsItem) {
        if (this.fields == null){
            fields = new ArrayList<>();
        }
        this.fields.add(fieldsItem);
        return this;
    }

    /**
    * Get multipleExtend
    * @return multipleExtend
    **/
    @JsonProperty("MultipleExtend")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<String> getMultipleExtend() {
        return multipleExtend;
    }

    /**
     * Set multipleExtend
     **/
    public void setMultipleExtend(List<String> multipleExtend) {
        this.multipleExtend = multipleExtend;
    }

    public CodeDataStruct multipleExtend(List<String> multipleExtend) {
        this.multipleExtend = multipleExtend;
        return this;
    }
    public CodeDataStruct addMultipleExtendItem(String multipleExtendItem) {
        if (this.multipleExtend == null){
            multipleExtend = new ArrayList<>();
        }
        this.multipleExtend.add(multipleExtendItem);
        return this;
    }

    /**
    * Get _implements
    * @return _implements
    **/
    @JsonProperty("Implements")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<String> getImplements() {
        return _implements;
    }

    /**
     * Set _implements
     **/
    public void setImplements(List<String> _implements) {
        this._implements = _implements;
    }

    public CodeDataStruct _implements(List<String> _implements) {
        this._implements = _implements;
        return this;
    }
    public CodeDataStruct addImplementsItem(String _implementsItem) {
        if (this._implements == null){
            _implements = new ArrayList<>();
        }
        this._implements.add(_implementsItem);
        return this;
    }

    /**
    * Get extend
    * @return extend
    **/
    @JsonProperty("Extend")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public String getExtend() {
        return extend;
    }

    /**
     * Set extend
     **/
    public void setExtend(String extend) {
        this.extend = extend;
    }

    public CodeDataStruct extend(String extend) {
        this.extend = extend;
        return this;
    }

    /**
    * Get functions
    * @return functions
    **/
    @JsonProperty("Functions")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<CodeFunction> getFunctions() {
        return functions;
    }

    /**
     * Set functions
     **/
    public void setFunctions(List<CodeFunction> functions) {
        this.functions = functions;
    }

    public CodeDataStruct functions(List<CodeFunction> functions) {
        this.functions = functions;
        return this;
    }
    public CodeDataStruct addFunctionsItem(CodeFunction functionsItem) {
        if (this.functions == null){
            functions = new ArrayList<>();
        }
        this.functions.add(functionsItem);
        return this;
    }

    /**
    * Get innerStructures
    * @return innerStructures
    **/
    @JsonProperty("InnerStructures")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<CodeDataStruct> getInnerStructures() {
        return innerStructures;
    }

    /**
     * Set innerStructures
     **/
    public void setInnerStructures(List<CodeDataStruct> innerStructures) {
        this.innerStructures = innerStructures;
    }

    public CodeDataStruct innerStructures(List<CodeDataStruct> innerStructures) {
        this.innerStructures = innerStructures;
        return this;
    }
    public CodeDataStruct addInnerStructuresItem(CodeDataStruct innerStructuresItem) {
        if (this.innerStructures == null){
            innerStructures = new ArrayList<>();
        }
        this.innerStructures.add(innerStructuresItem);
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

    public CodeDataStruct annotations(List<CodeAnnotation> annotations) {
        this.annotations = annotations;
        return this;
    }
    public CodeDataStruct addAnnotationsItem(CodeAnnotation annotationsItem) {
        if (this.annotations == null){
            annotations = new ArrayList<>();
        }
        this.annotations.add(annotationsItem);
        return this;
    }

    /**
    * Get functionCalls
    * @return functionCalls
    **/
    @JsonProperty("FunctionCalls")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<CodeCall> getFunctionCalls() {
        return functionCalls;
    }

    /**
     * Set functionCalls
     **/
    public void setFunctionCalls(List<CodeCall> functionCalls) {
        this.functionCalls = functionCalls;
    }

    public CodeDataStruct functionCalls(List<CodeCall> functionCalls) {
        this.functionCalls = functionCalls;
        return this;
    }
    public CodeDataStruct addFunctionCallsItem(CodeCall functionCallsItem) {
        if (this.functionCalls == null){
            functionCalls = new ArrayList<>();
        }
        this.functionCalls.add(functionCallsItem);
        return this;
    }

    /**
    * Get parameters
    * @return parameters
    **/
    @JsonProperty("Parameters")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<CodeProperty> getParameters() {
        return parameters;
    }

    /**
     * Set parameters
     **/
    public void setParameters(List<CodeProperty> parameters) {
        this.parameters = parameters;
    }

    public CodeDataStruct parameters(List<CodeProperty> parameters) {
        this.parameters = parameters;
        return this;
    }
    public CodeDataStruct addParametersItem(CodeProperty parametersItem) {
        if (this.parameters == null){
            parameters = new ArrayList<>();
        }
        this.parameters.add(parametersItem);
        return this;
    }

    /**
    * Get imports
    * @return imports
    **/
    @JsonProperty("Imports")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<CodeImport> getImports() {
        return imports;
    }

    /**
     * Set imports
     **/
    public void setImports(List<CodeImport> imports) {
        this.imports = imports;
    }

    public CodeDataStruct imports(List<CodeImport> imports) {
        this.imports = imports;
        return this;
    }
    public CodeDataStruct addImportsItem(CodeImport importsItem) {
        if (this.imports == null){
            imports = new ArrayList<>();
        }
        this.imports.add(importsItem);
        return this;
    }

    /**
    * Get exports
    * @return exports
    **/
    @JsonProperty("Exports")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public List<CodeExport> getExports() {
        return exports;
    }

    /**
     * Set exports
     **/
    public void setExports(List<CodeExport> exports) {
        this.exports = exports;
    }

    public CodeDataStruct exports(List<CodeExport> exports) {
        this.exports = exports;
        return this;
    }
    public CodeDataStruct addExportsItem(CodeExport exportsItem) {
        if (this.exports == null){
            exports = new ArrayList<>();
        }
        this.exports.add(exportsItem);
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

    public CodeDataStruct extension(String extension) {
        this.extension = extension;
        return this;
    }

    /**
    * Get position
    * @return position
    **/
    @JsonProperty("Position")
          @com.fasterxml.jackson.annotation.JsonInclude(com.fasterxml.jackson.annotation.JsonInclude.Include.NON_NULL)
    public CodePosition getPosition() {
        return position;
    }

    /**
     * Set position
     **/
    public void setPosition(CodePosition position) {
        this.position = position;
    }

    public CodeDataStruct position(CodePosition position) {
        this.position = position;
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

    public CodeDataStruct content(String content) {
        this.content = content;
        return this;
    }

    /**
     * Create a string representation of this pojo.
     **/
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("class CodeDataStruct {\n");

        sb.append("    nodeName: ").append(toIndentedString(nodeName)).append("\n");
        sb.append("    module: ").append(toIndentedString(module)).append("\n");
        sb.append("    type: ").append(toIndentedString(type)).append("\n");
        sb.append("    _package: ").append(toIndentedString(_package)).append("\n");
        sb.append("    filePath: ").append(toIndentedString(filePath)).append("\n");
        sb.append("    fields: ").append(toIndentedString(fields)).append("\n");
        sb.append("    multipleExtend: ").append(toIndentedString(multipleExtend)).append("\n");
        sb.append("    _implements: ").append(toIndentedString(_implements)).append("\n");
        sb.append("    extend: ").append(toIndentedString(extend)).append("\n");
        sb.append("    functions: ").append(toIndentedString(functions)).append("\n");
        sb.append("    innerStructures: ").append(toIndentedString(innerStructures)).append("\n");
        sb.append("    annotations: ").append(toIndentedString(annotations)).append("\n");
        sb.append("    functionCalls: ").append(toIndentedString(functionCalls)).append("\n");
        sb.append("    parameters: ").append(toIndentedString(parameters)).append("\n");
        sb.append("    imports: ").append(toIndentedString(imports)).append("\n");
        sb.append("    exports: ").append(toIndentedString(exports)).append("\n");
        sb.append("    extension: ").append(toIndentedString(extension)).append("\n");
        sb.append("    position: ").append(toIndentedString(position)).append("\n");
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
    public static class CodeDataStructQueryParam  {

        @jakarta.ws.rs.QueryParam("nodeName")
        private String nodeName;
        @jakarta.ws.rs.QueryParam("module")
        private String module;
        @jakarta.ws.rs.QueryParam("type")
        private String type;
        @jakarta.ws.rs.QueryParam("_package")
        private String _package;
        @jakarta.ws.rs.QueryParam("filePath")
        private String filePath;
        @jakarta.ws.rs.QueryParam("fields")
        private List<CodeField> fields = null;
        @jakarta.ws.rs.QueryParam("multipleExtend")
        private List<String> multipleExtend = null;
        @jakarta.ws.rs.QueryParam("_implements")
        private List<String> _implements = null;
        @jakarta.ws.rs.QueryParam("extend")
        private String extend;
        @jakarta.ws.rs.QueryParam("functions")
        private List<CodeFunction> functions = null;
        @jakarta.ws.rs.QueryParam("innerStructures")
        private List<CodeDataStruct> innerStructures = null;
        @jakarta.ws.rs.QueryParam("annotations")
        private List<CodeAnnotation> annotations = null;
        @jakarta.ws.rs.QueryParam("functionCalls")
        private List<CodeCall> functionCalls = null;
        @jakarta.ws.rs.QueryParam("parameters")
        private List<CodeProperty> parameters = null;
        @jakarta.ws.rs.QueryParam("imports")
        private List<CodeImport> imports = null;
        @jakarta.ws.rs.QueryParam("exports")
        private List<CodeExport> exports = null;
        @jakarta.ws.rs.QueryParam("extension")
        private String extension;
        @jakarta.ws.rs.QueryParam("position")
        private CodePosition position;
        @jakarta.ws.rs.QueryParam("content")
        private String content;

        /**
        * Get nodeName
        * @return nodeName
        **/
        @JsonProperty("NodeName")
        public String getNodeName() {
            return nodeName;
        }

        /**
         * Set nodeName
         **/
        public void setNodeName(String nodeName) {
            this.nodeName = nodeName;
        }

        public CodeDataStructQueryParam nodeName(String nodeName) {
            this.nodeName = nodeName;
            return this;
        }

        /**
        * Get module
        * @return module
        **/
        @JsonProperty("Module")
        public String getModule() {
            return module;
        }

        /**
         * Set module
         **/
        public void setModule(String module) {
            this.module = module;
        }

        public CodeDataStructQueryParam module(String module) {
            this.module = module;
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

        public CodeDataStructQueryParam type(String type) {
            this.type = type;
            return this;
        }

        /**
        * Get _package
        * @return _package
        **/
        @JsonProperty("Package")
        public String getPackage() {
            return _package;
        }

        /**
         * Set _package
         **/
        public void setPackage(String _package) {
            this._package = _package;
        }

        public CodeDataStructQueryParam _package(String _package) {
            this._package = _package;
            return this;
        }

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

        public CodeDataStructQueryParam filePath(String filePath) {
            this.filePath = filePath;
            return this;
        }

        /**
        * Get fields
        * @return fields
        **/
        @JsonProperty("Fields")
        public List<CodeField> getFields() {
            return fields;
        }

        /**
         * Set fields
         **/
        public void setFields(List<CodeField> fields) {
            this.fields = fields;
        }

        public CodeDataStructQueryParam fields(List<CodeField> fields) {
            this.fields = fields;
            return this;
        }
        public CodeDataStructQueryParam addFieldsItem(CodeField fieldsItem) {
            this.fields.add(fieldsItem);
            return this;
        }

        /**
        * Get multipleExtend
        * @return multipleExtend
        **/
        @JsonProperty("MultipleExtend")
        public List<String> getMultipleExtend() {
            return multipleExtend;
        }

        /**
         * Set multipleExtend
         **/
        public void setMultipleExtend(List<String> multipleExtend) {
            this.multipleExtend = multipleExtend;
        }

        public CodeDataStructQueryParam multipleExtend(List<String> multipleExtend) {
            this.multipleExtend = multipleExtend;
            return this;
        }
        public CodeDataStructQueryParam addMultipleExtendItem(String multipleExtendItem) {
            this.multipleExtend.add(multipleExtendItem);
            return this;
        }

        /**
        * Get _implements
        * @return _implements
        **/
        @JsonProperty("Implements")
        public List<String> getImplements() {
            return _implements;
        }

        /**
         * Set _implements
         **/
        public void setImplements(List<String> _implements) {
            this._implements = _implements;
        }

        public CodeDataStructQueryParam _implements(List<String> _implements) {
            this._implements = _implements;
            return this;
        }
        public CodeDataStructQueryParam addImplementsItem(String _implementsItem) {
            this._implements.add(_implementsItem);
            return this;
        }

        /**
        * Get extend
        * @return extend
        **/
        @JsonProperty("Extend")
        public String getExtend() {
            return extend;
        }

        /**
         * Set extend
         **/
        public void setExtend(String extend) {
            this.extend = extend;
        }

        public CodeDataStructQueryParam extend(String extend) {
            this.extend = extend;
            return this;
        }

        /**
        * Get functions
        * @return functions
        **/
        @JsonProperty("Functions")
        public List<CodeFunction> getFunctions() {
            return functions;
        }

        /**
         * Set functions
         **/
        public void setFunctions(List<CodeFunction> functions) {
            this.functions = functions;
        }

        public CodeDataStructQueryParam functions(List<CodeFunction> functions) {
            this.functions = functions;
            return this;
        }
        public CodeDataStructQueryParam addFunctionsItem(CodeFunction functionsItem) {
            this.functions.add(functionsItem);
            return this;
        }

        /**
        * Get innerStructures
        * @return innerStructures
        **/
        @JsonProperty("InnerStructures")
        public List<CodeDataStruct> getInnerStructures() {
            return innerStructures;
        }

        /**
         * Set innerStructures
         **/
        public void setInnerStructures(List<CodeDataStruct> innerStructures) {
            this.innerStructures = innerStructures;
        }

        public CodeDataStructQueryParam innerStructures(List<CodeDataStruct> innerStructures) {
            this.innerStructures = innerStructures;
            return this;
        }
        public CodeDataStructQueryParam addInnerStructuresItem(CodeDataStruct innerStructuresItem) {
            this.innerStructures.add(innerStructuresItem);
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

        public CodeDataStructQueryParam annotations(List<CodeAnnotation> annotations) {
            this.annotations = annotations;
            return this;
        }
        public CodeDataStructQueryParam addAnnotationsItem(CodeAnnotation annotationsItem) {
            this.annotations.add(annotationsItem);
            return this;
        }

        /**
        * Get functionCalls
        * @return functionCalls
        **/
        @JsonProperty("FunctionCalls")
        public List<CodeCall> getFunctionCalls() {
            return functionCalls;
        }

        /**
         * Set functionCalls
         **/
        public void setFunctionCalls(List<CodeCall> functionCalls) {
            this.functionCalls = functionCalls;
        }

        public CodeDataStructQueryParam functionCalls(List<CodeCall> functionCalls) {
            this.functionCalls = functionCalls;
            return this;
        }
        public CodeDataStructQueryParam addFunctionCallsItem(CodeCall functionCallsItem) {
            this.functionCalls.add(functionCallsItem);
            return this;
        }

        /**
        * Get parameters
        * @return parameters
        **/
        @JsonProperty("Parameters")
        public List<CodeProperty> getParameters() {
            return parameters;
        }

        /**
         * Set parameters
         **/
        public void setParameters(List<CodeProperty> parameters) {
            this.parameters = parameters;
        }

        public CodeDataStructQueryParam parameters(List<CodeProperty> parameters) {
            this.parameters = parameters;
            return this;
        }
        public CodeDataStructQueryParam addParametersItem(CodeProperty parametersItem) {
            this.parameters.add(parametersItem);
            return this;
        }

        /**
        * Get imports
        * @return imports
        **/
        @JsonProperty("Imports")
        public List<CodeImport> getImports() {
            return imports;
        }

        /**
         * Set imports
         **/
        public void setImports(List<CodeImport> imports) {
            this.imports = imports;
        }

        public CodeDataStructQueryParam imports(List<CodeImport> imports) {
            this.imports = imports;
            return this;
        }
        public CodeDataStructQueryParam addImportsItem(CodeImport importsItem) {
            this.imports.add(importsItem);
            return this;
        }

        /**
        * Get exports
        * @return exports
        **/
        @JsonProperty("Exports")
        public List<CodeExport> getExports() {
            return exports;
        }

        /**
         * Set exports
         **/
        public void setExports(List<CodeExport> exports) {
            this.exports = exports;
        }

        public CodeDataStructQueryParam exports(List<CodeExport> exports) {
            this.exports = exports;
            return this;
        }
        public CodeDataStructQueryParam addExportsItem(CodeExport exportsItem) {
            this.exports.add(exportsItem);
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

        public CodeDataStructQueryParam extension(String extension) {
            this.extension = extension;
            return this;
        }

        /**
        * Get position
        * @return position
        **/
        @JsonProperty("Position")
        public CodePosition getPosition() {
            return position;
        }

        /**
         * Set position
         **/
        public void setPosition(CodePosition position) {
            this.position = position;
        }

        public CodeDataStructQueryParam position(CodePosition position) {
            this.position = position;
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

        public CodeDataStructQueryParam content(String content) {
            this.content = content;
            return this;
        }

        /**
         * Create a string representation of this pojo.
         **/
        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("class CodeDataStructQueryParam {\n");

            sb.append("    nodeName: ").append(toIndentedString(nodeName)).append("\n");
            sb.append("    module: ").append(toIndentedString(module)).append("\n");
            sb.append("    type: ").append(toIndentedString(type)).append("\n");
            sb.append("    _package: ").append(toIndentedString(_package)).append("\n");
            sb.append("    filePath: ").append(toIndentedString(filePath)).append("\n");
            sb.append("    fields: ").append(toIndentedString(fields)).append("\n");
            sb.append("    multipleExtend: ").append(toIndentedString(multipleExtend)).append("\n");
            sb.append("    _implements: ").append(toIndentedString(_implements)).append("\n");
            sb.append("    extend: ").append(toIndentedString(extend)).append("\n");
            sb.append("    functions: ").append(toIndentedString(functions)).append("\n");
            sb.append("    innerStructures: ").append(toIndentedString(innerStructures)).append("\n");
            sb.append("    annotations: ").append(toIndentedString(annotations)).append("\n");
            sb.append("    functionCalls: ").append(toIndentedString(functionCalls)).append("\n");
            sb.append("    parameters: ").append(toIndentedString(parameters)).append("\n");
            sb.append("    imports: ").append(toIndentedString(imports)).append("\n");
            sb.append("    exports: ").append(toIndentedString(exports)).append("\n");
            sb.append("    extension: ").append(toIndentedString(extension)).append("\n");
            sb.append("    position: ").append(toIndentedString(position)).append("\n");
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