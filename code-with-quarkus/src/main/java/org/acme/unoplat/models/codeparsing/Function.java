package org.acme.unoplat.models.codeparsing; 
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.ArrayList;
import java.util.List; 


import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Setter
@Getter
@AllArgsConstructor
@NoArgsConstructor
public class Function{
    @JsonProperty("Name")
    private String name;
    @JsonProperty("ReturnType")
    private String returnType;
    @JsonProperty("Parameters")
    private ArrayList<Parameter> parameters;
    @JsonProperty("FunctionCalls")
    private ArrayList<FunctionCall> functionCalls;
    @JsonProperty("Position")
    private Position position;
    @JsonProperty("LocalVariables")
    private ArrayList<LocalVariable> localVariables;
    @JsonProperty("BodyHash")
    private int bodyHash;
    @JsonProperty("Content")
    private String content;
}
