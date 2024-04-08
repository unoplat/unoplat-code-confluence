package org.acme;

import io.quarkiverse.openapi.generator.annotations.GeneratedMethod;
import io.quarkiverse.openapi.generator.annotations.GeneratedParam;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.openapi.quarkus.archguard_yaml.api.DefaultApi;
import org.openapi.quarkus.archguard_yaml.model.CodeDataStruct;


@ApplicationScoped
public class GreetingResource implements DefaultApi {

    private String systemId;
    private String language;
    private String path;
    private String repoId;
    private CodeDataStruct codeDataStruct;

    @Override
    @POST
    @Consumes({"application/json"})
    @GeneratedMethod("")
    public jakarta.ws.rs.core.Response classItemsPost(
  @GeneratedParam("systemId") @PathParam("systemId") String systemId
, @GeneratedParam("language") @QueryParam("language") String language
, @GeneratedParam("path") @QueryParam("path") String path
, @GeneratedParam("repoId") @QueryParam("repoId") String repoId
, CodeDataStruct codeDataStruct)
{
    this.systemId = systemId;
    this.language = language;
    this.path = path;
    this.repoId = repoId;
    this.codeDataStruct = codeDataStruct;
    System.out.println("Saving CodeDataStruct for systemId: " + systemId + ", language: " + language);
        
// Assuming the save operation is successful
    return Response.ok().build();
}
    
}
