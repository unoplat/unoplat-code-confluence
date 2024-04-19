package org.acme.unoplat.processor.transform.impl;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import jakarta.inject.Singleton;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import org.acme.unoplat.models.codeparsing.Function;
import org.acme.unoplat.models.codeparsing.Root;
import org.acme.unoplat.processor.comments.CommentsExtractor;
import org.acme.unoplat.processor.transform.InPlaceTransformCodeMeta;
import org.jboss.logging.Logger;

import io.smallrye.mutiny.Multi;
import io.smallrye.mutiny.Uni;

@ApplicationScoped
public class InPlaceTransformCodeMetaImpl implements InPlaceTransformCodeMeta {

    private static Logger LOG = Logger.getLogger(InPlaceTransformCodeMeta.class);

    @Inject
    @Named("JavaCommentParser")
    private CommentsExtractor commentsExtractor;

    // TODO: make this method figure out type of programming language automatically
    // and use then appropriate comment extractor
    @Override
    public List<Root> modifyMetadata(List<Root> rootList) {
        Multi<Root> roots = Multi.createFrom().iterable(rootList);
        return roots.onItem().transform(root -> processRoot(root))
                .collect().asList()
                .await().indefinitely();
    }

    private Root processRoot(Root root) {
        if (root.getContent() != null) {
            String extractedContent = commentsExtractor.getComments(root.getContent());
            // Check if the extracted content is null or empty after comment extraction
            if (extractedContent != null && !extractedContent.isEmpty()) {
                root.setContent(extractedContent);
            } else {
                LOG.warn("Extracted content is null or empty after processing. Original content retained.");
            }
        } else {
            LOG.warn("Root content is null, skipping comment extraction.");
        }

        if (root.getFunctions() != null) {
            root.setFunctions(processFunctions(root.getFunctions()));
        } else {
            LOG.warn("Function list is null, skipping processing.");
        }
        return root;
    }

    private ArrayList<Function> processFunctions(List<Function> functions) {
        return new ArrayList<>(Multi.createFrom().iterable(functions)
                    .onItem().transform(this::processFunction)
                    .collect().asList()
                    .await().indefinitely());
    }

    private Function processFunction(Function function) {
        if (function.getContent() != null) {
            String extractedContent = commentsExtractor.getComments(function.getContent());
            // Check if the extracted content is null or empty
            if (extractedContent != null && !extractedContent.isEmpty()) {
                function.setContent(extractedContent);
            } else {
                LOG.warn("Extracted function content is null or empty after processing. Original content retained.");
            }
        } else {
            LOG.warn("Function content is null, skipping comment extraction.");
        }
        return function;
    }

}
