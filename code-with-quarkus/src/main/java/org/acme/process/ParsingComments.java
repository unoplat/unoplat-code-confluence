package org.acme.process;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.ApplicationPath;
import org.acme.unoplat.models.codeparsing.Function;
import org.acme.unoplat.models.codeparsing.Root;

import java.util.List;

@ApplicationScoped
public class ParsingComments {

    public void parseInLineContentForCode(List<Root> rootList)
    {
        for(Root root: rootList)
        {
            for(Function function: root.getFunctions())
            {
                    
            }
        }
    }
}
