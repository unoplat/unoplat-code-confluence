package org.acme;

import jakarta.ws.rs.QueryParam;
import org.acme.unoplat.models.model.CodeDataStruct;
import org.jboss.logging.Logger;

import io.smallrye.common.constraint.NotNull;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("api/scanner/{systemId}/reporting/class-items")
public class ScannerReportingResource {
    private static final Logger LOG = Logger.getLogger(ScannerReportingResource.class);

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    public Response saveClassItems(@PathParam("systemId") String systemId, @QueryParam("language") String language, @QueryParam("path") String path, @NotNull CodeDataStruct[] codeDataStruct) {
        // Here you would include your logic to process the CodeDataStruct object
        // For example, saving it to a database or performing some analysis
        LOG.infof("Received class items for system ID %s, Language: %s, Path: %s: %s", systemId, language, path, codeDataStruct);
        LOG.infof("Main class info is %s",codeDataStruct[0].getContent());
        // Returning a simple response for demonstration purposes
        return Response.ok().entity(String.format("Data for system ID %s, Language: %s, Path: %s received and processed.", systemId, language, path)).build();
    }
}
