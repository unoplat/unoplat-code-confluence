package org.acme.unoplat.models.codeparsing; 
import com.fasterxml.jackson.annotation.JsonProperty; 
public class Position{
    @JsonProperty("StartLine") 
    public int startLine;
    @JsonProperty("StartLinePosition") 
    public int startLinePosition;
    @JsonProperty("StopLine") 
    public int stopLine;
    @JsonProperty("StopLinePosition") 
    public int stopLinePosition;
}
