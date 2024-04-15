package org.acme.exception;

import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerResponseContext;
import jakarta.ws.rs.container.ContainerResponseFilter;
import jakarta.ws.rs.ext.Provider;
import java.io.IOException;
import org.jboss.logging.Logger;

@Provider
public class ResponseFilter implements ContainerResponseFilter {

    private static Logger LOG = Logger.getLogger(ResponseFilter.class);
    @Override
    public void filter(ContainerRequestContext containerRequestContext,
                       ContainerResponseContext containerResponseContext) throws IOException {

        LOG.infof("Status is: %d ",containerResponseContext.getStatus());
        LOG.infof("Entity is: %s ",containerResponseContext.getEntity());

    }
}
