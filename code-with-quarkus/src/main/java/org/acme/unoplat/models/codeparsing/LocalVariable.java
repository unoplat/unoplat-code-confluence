package org.acme.unoplat.models.codeparsing; 
import com.fasterxml.jackson.annotation.JsonProperty; 
public class LocalVariable{
    @JsonProperty("TypeValue") 
    public String typeValue;
    @JsonProperty("TypeType") 
    public String typeType;
}
