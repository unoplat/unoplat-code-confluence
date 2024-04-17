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
public class FunctionCall{
    @JsonProperty("Package")
    private String packageName;
    @JsonProperty("NodeName")
    private String nodeName;
    @JsonProperty("FunctionName")
    private String functionName;
    @JsonProperty("Parameters")
    private ArrayList<Parameter> parameters;
    @JsonProperty("Position")
    private Position position;
    @JsonProperty("Type")
    private String type;
}
