package org.acme.unoplat.models.codeparsing; 
import com.fasterxml.jackson.annotation.JsonProperty; 
public class Annotation{
    @JsonProperty("Name") 
    public String name;
    @JsonProperty("Position") 
    public Position position;
}
