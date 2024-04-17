package org.acme.unoplat.models.codeparsing; 
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.ArrayList;
import java.util.List; 
public class FunctionCall{
    @JsonProperty("Package") 
    public String packageName;
    @JsonProperty("NodeName") 
    public String nodeName;
    @JsonProperty("FunctionName") 
    public String functionName;
    @JsonProperty("Parameters") 
    public ArrayList<Parameter> parameters;
    @JsonProperty("Position") 
    public Position position;
    @JsonProperty("Type") 
    public String type;
}
