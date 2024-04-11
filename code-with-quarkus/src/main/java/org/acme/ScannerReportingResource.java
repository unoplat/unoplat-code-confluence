package org.acme;

import org.acme.unoplat.models.model.CodeDataStruct;
import org.jboss.logging.Logger;

import io.smallrye.common.constraint.NotNull;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/scanner/{systemId}/reporting/class-items")
public class ScannerReportingResource {
    private static final Logger LOG = Logger.getLogger(ScannerReportingResource.class);

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    public Response saveClassItems(@PathParam("systemId") String systemId,@NotNull CodeDataStruct codeDataStruct) {
        // Here you would include your logic to process the CodeDataStruct object
        // For example, saving it to a database or performing some analysis
        LOG.infof("Received class items for system ID %s: %s", systemId, codeDataStruct);
        // Returning a simple response for demonstration purposes
        return Response.ok().entity("Data for system ID " + systemId + " received and processed.").build();
    }
}
