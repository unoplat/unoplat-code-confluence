package org.acme.unoplat.processor.transform;

import java.util.List;
import org.acme.unoplat.models.codeparsing.Root;

public interface InPlaceTransformCodeMeta {

    public List<Root> modifyMetadata(List<Root> rootList);

}
