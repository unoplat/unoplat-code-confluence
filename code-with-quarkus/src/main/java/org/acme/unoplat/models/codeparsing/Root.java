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
public class Root{
    @JsonProperty("NodeName")
    private String nodeName;
    @JsonProperty("Module")
    private String module;
    @JsonProperty("Type")
    private String type;
    @JsonProperty("Package")
    private String packageName;
    @JsonProperty("FilePath")
    private String filePath;
    @JsonProperty("Functions")
    private ArrayList<Function> functions;
    @JsonProperty("Annotations")
    private ArrayList<Annotation> annotations;
    @JsonProperty("Imports")
    private ArrayList<Import> imports;
    @JsonProperty("Position")
    private Position position;
    @JsonProperty("Content")
    private String content;
}
