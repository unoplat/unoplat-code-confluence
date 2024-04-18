package org.acme;

import jakarta.inject.Inject;
import jakarta.ws.rs.QueryParam;

import java.util.Arrays;
import java.util.List;
import org.acme.unoplat.models.codeparsing.Root;
import org.acme.unoplat.processor.transform.InPlaceTransformCodeMeta;
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


    @Inject
    private InPlaceTransformCodeMeta inPlaceTransformCodeMeta;

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    public Response saveClassItems(@PathParam("systemId") String systemId, @QueryParam("language") String language, @QueryParam("path") String path, @NotNull Root[] codeDataStruct) {
        // Here you would include your logic to process the CodeDataStruct object
        // For example, saving it to a database or performing some analysis
        LOG.infof("Received class items for system ID %s, Language: %s, Path: %s: %s", systemId, language, path, codeDataStruct);
        LOG.infof("Main class info is %s",codeDataStruct[0].getContent());
        LOG.infof("Function  info is %s",codeDataStruct[0].getFunctions().get(0).getContent());

        List<Root> root = inPlaceTransformCodeMeta.modifyMetadata(Arrays.asList(codeDataStruct));

        return Response.ok(root).build();  // Automatically converts List<Root> into JSON
    }
}
