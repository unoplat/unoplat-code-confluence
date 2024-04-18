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
        // Transforming class content
        String classComment = commentsExtractor.getComments(root.getContent());
        root.setContent(classComment);
        List<Function> functions = root.getFunctions();
        if (functions != null) {
        
        // Transforming function content
        Multi<Function> multiFunctions = Multi.createFrom().iterable(root.getFunctions());

        List<Function> rootFunctions = multiFunctions.onItem().transform(function -> processFunction( function))
                .collect().asList()
                .await().indefinitely();
        root.setFunctions(new ArrayList<>(rootFunctions));
        }
        
        return root;

    }

    private Function processFunction( Function function) {
        // Transforming function content
        String functionComment = commentsExtractor.getComments(function.getContent());
        // Transforming function content
        function.setContent(functionComment);

        return function;
    }
}
