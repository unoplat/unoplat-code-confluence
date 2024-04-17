package org.acme.unoplat.models.codeparsing; 

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Setter
@Getter
@AllArgsConstructor
@NoArgsConstructor
public class Annotation{
    @JsonProperty("Name") 
    private String name;
    @JsonProperty("Position")
    private Position position;
}
