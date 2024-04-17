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
public class Position{
    @JsonProperty("StartLine")
    private int startLine;
    @JsonProperty("StartLinePosition")
    private int startLinePosition;
    @JsonProperty("StopLine")
    private int stopLine;
    @JsonProperty("StopLinePosition")
    private int stopLinePosition;
}
