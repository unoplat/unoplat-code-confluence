package org.acme.exception;



import io.vertx.core.Future;
import io.vertx.core.buffer.Buffer;
import io.vertx.core.http.HttpServerRequest;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerRequestFilter;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.core.HttpHeaders;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.core.UriInfo;
import jakarta.ws.rs.ext.Provider;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import org.jboss.logging.Logger;

@Provider
public class BadRequestExceptionMapper implements ContainerRequestFilter {

    private static Logger LOG = Logger.getLogger(BadRequestExceptionMapper.class);

    @Context
    private UriInfo uriInfo;

    @Context
    HttpServerRequest request;


    @Override
    public void filter(ContainerRequestContext containerRequestContext) throws IOException {

        final String method = containerRequestContext.getMethod();
        final String path = uriInfo.getPath();
        final String address = request.remoteAddress().toString();
        LOG.info("Headers:" + request.headers().toString());

        Future<Buffer> futureBody = request.body();
        futureBody.onComplete(asyncResult -> {
            if (asyncResult.succeeded()) {
                String bodyContent = asyncResult.result().toString();
                LOG.debug("Body: " + bodyContent);

                // Write body content as string into file
                try {
                    Files.write(Paths.get("input-request-body.json"), bodyContent.getBytes(), StandardOpenOption.CREATE);
                } catch (IOException e) {
                    LOG.error("Error while writing body to file: ", e);
                }

            } else {
                LOG.info("Error while reading body: ", asyncResult.cause());
            }
        });

        LOG.infof("Request %s %s from IP %s", method, path, address);
    }
}
