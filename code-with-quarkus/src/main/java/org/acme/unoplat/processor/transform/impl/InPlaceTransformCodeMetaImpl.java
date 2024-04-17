package org.acme.unoplat.processor.transform.impl;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.util.List;
import java.util.stream.Collectors;
import org.acme.unoplat.models.codeparsing.Root;
import org.acme.unoplat.processor.comments.CommentsExtractor;
import org.acme.unoplat.processor.transform.InPlaceTransformCodeMeta;
import org.jboss.logging.Logger;

@Singleton
public class InPlaceTransformCodeMetaImpl  implements InPlaceTransformCodeMeta {

    private static Logger LOG = Logger.getLogger(InPlaceTransformCodeMeta.class);

    @Inject
    @Named("JavaCommentParser")
    private CommentsExtractor commentsExtractor;

    //TODO: make this method figure out type of programming language automatically and use then appropriate comment extractor
    @Override
    public List<Root> modifyMetadata(List<Root> rootList) {

            return rootList.parallelStream()
                    .map(this::processRoot)
                    .collect(Collectors.toList());
        }

        private Root processRoot(Root root) {
            // Include your logic to process a Root object here
            // For example, let's just return the same root object without modifying it
            String comment = commentsExtractor.getComments(root.getContent());
            LOG.infof("comment is %s",comment);
            return root;
        }
    }

