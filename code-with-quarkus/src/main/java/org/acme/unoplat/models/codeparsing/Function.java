package org.acme.unoplat.models.codeparsing; 
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.ArrayList;
import java.util.List; 
public class Function{
    @JsonProperty("Name") 
    public String name;
    @JsonProperty("ReturnType") 
    public String returnType;
    @JsonProperty("Parameters") 
    public ArrayList<Parameter> parameters;
    @JsonProperty("FunctionCalls") 
    public ArrayList<FunctionCall> functionCalls;
    @JsonProperty("Position") 
    public Position position;
    @JsonProperty("LocalVariables") 
    public ArrayList<LocalVariable> localVariables;
    @JsonProperty("BodyHash") 
    public int bodyHash;
    @JsonProperty("Content") 
    public String content;
}
