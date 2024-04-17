package org.acme.unoplat.models.codeparsing; 
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.ArrayList;
import java.util.List; 
public class Root{
    @JsonProperty("NodeName") 
    public String nodeName;
    @JsonProperty("Module") 
    public String module;
    @JsonProperty("Type") 
    public String type;
    @JsonProperty("Package") 
    public String packageName;
    @JsonProperty("FilePath") 
    public String filePath;
    @JsonProperty("Functions") 
    public ArrayList<Function> functions;
    @JsonProperty("Annotations") 
    public ArrayList<Annotation> annotations;
    @JsonProperty("Imports") 
    public ArrayList<Import> imports;
    @JsonProperty("Position") 
    public Position position;
    @JsonProperty("Content") 
    public String content;
}
