package org.acme.unoplat.processor.comments.impl;


import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import jakarta.ws.rs.ApplicationPath;

import java.io.FileWriter;
import java.io.IOException;
import java.io.StringReader;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.acme.unoplat.processor.comments.CommentsExtractor;
import org.jboss.logging.Logger;

@Named(value = "JavaCommentParser")
@ApplicationScoped
public class JavaCommentsExtractor  implements CommentsExtractor {

    
    private static Logger LOG = Logger.getLogger(JavaCommentsExtractor.class);

    @Override
    public String getComments(String content) {

        //todo: get comments out of java class that is in content
        LOG.infof("Content is:%s", content);
        String regex = "/\\*\\*[^*]*\\*+(?:[^/*][^*]*\\*+)*/";

        Pattern pattern = Pattern.compile(regex, Pattern.DOTALL);
        Matcher matcher = pattern.matcher(content);

        StringBuilder comments = new StringBuilder();
        while (matcher.find()) {
            comments.append(matcher.group()).append("\n\n");  // Concatenating comments with a newline
        }
        String cleanedComment = comments.toString().replaceAll("[^a-zA-Z0-9\\s.]", " ").replaceAll("\\.\\s+", ". ");
        
        LOG.infof("Comments are:%s", cleanedComment);
        //write comments to a file and keep appending through a separator in text file
      
        return cleanedComment;
    }


}
