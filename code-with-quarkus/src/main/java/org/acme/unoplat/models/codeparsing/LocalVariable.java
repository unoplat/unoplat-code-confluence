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
public class LocalVariable{
    @JsonProperty("TypeValue")
    private String typeValue;
    @JsonProperty("TypeType")
    private String typeType;
}
