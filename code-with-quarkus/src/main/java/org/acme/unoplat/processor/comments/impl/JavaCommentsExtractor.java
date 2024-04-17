package org.acme.unoplat.processor.comments.impl;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.Problem;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.comments.Comment;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.util.List;
import org.acme.unoplat.processor.comments.CommentsExtractor;
import org.jboss.logging.Logger;

@Named(value = "JavaCommentParser")
@Singleton
public class JavaCommentsExtractor  implements CommentsExtractor {

    @Inject
    private JavaParser javaParser;

    private static Logger LOG = Logger.getLogger(JavaCommentsExtractor.class);

    @Override
    public String getComments(String content) {

        //todo: get comments out of java class that is in content
        LOG.debugf("Content is:%s", content);
        if(javaParser == null)
        {
            LOG.error("java parser is null");
            System.exit(1);
        }
        ParseResult<CompilationUnit> parseResult = javaParser.parse(content);

        LOG.infof("ParseResult success %b",parseResult.isSuccessful());
        if (!parseResult.isSuccessful()) {
            List<Problem> problems = parseResult.getProblems();
            for (Problem problem : problems) {
                System.out.println(problem.getVerboseMessage());
            }
        }

        if (parseResult.isSuccessful()) {
            CompilationUnit cu = parseResult.getResult().get();
            Boolean hasRange = cu.hasRange();
            LOG.infof("hasRange: %",hasRange);
            StringBuilder comments = new StringBuilder();
            if (cu.hasRange()) {
                for (Comment comment : cu.getAllComments()) {
                    comments.append(comment.getContent()).append("\n");
                }
                return comments.toString();
            }
        } else {
            // Handle parsing error
            return null;
        }
        return null;
    }
}
