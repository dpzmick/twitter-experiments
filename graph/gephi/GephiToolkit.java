import java.io.File;
import java.io.IOException;
import org.gephi.data.attributes.api.AttributeColumn;
import org.gephi.data.attributes.api.AttributeController;
import org.gephi.data.attributes.api.AttributeModel;
import org.gephi.graph.api.DirectedGraph;
import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.EdgeDefault;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.openord.OpenOrdLayout;
import org.gephi.partition.api.Partition;
import org.gephi.partition.api.PartitionController;
import org.gephi.partition.plugin.NodeColorTransformer;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.gephi.ranking.api.Ranking;
import org.gephi.ranking.api.RankingController;
import org.gephi.ranking.api.Transformer;
import org.gephi.ranking.plugin.transformer.AbstractSizeTransformer;
import org.gephi.statistics.plugin.Modularity;
import org.openide.util.Lookup;
import org.gephi.statistics.plugin.GraphDistance;


public class GephiToolkit {

    public static void main(String[] args) {
        // Init a project - and therefore a workspace
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        // Get controllers and models
        ImportController importController = Lookup.getDefault().lookup(ImportController.class);
        GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getModel();
        AttributeModel attributeModel = Lookup.getDefault().lookup(AttributeController.class).getModel();
        DirectedGraph graph = graphModel.getDirectedGraph();
        RankingController rankingController = Lookup.getDefault().lookup(RankingController.class);

        // Import file
        Container container;
        try {
            System.out.println("Loading file");
            File file = new File("/Users/dz0004455/programming/ncsa/graph/csv/zero.csv");
            System.out.println("File loaded, Importing");
            container = importController.importFile(file);
            container.getLoader().setEdgeDefault(EdgeDefault.DIRECTED);
        } catch (Exception ex) {
            ex.printStackTrace();
            return;
        }
        System.out.println("imported");

        // Append imported data to GraphAPI
        importController.process(container, new DefaultProcessor(), workspace);

        // Run OpenOrd
        // Liquid 24 %
        // Expansion 75%
        // Cooldown 1%
        // Crunch 0
        // Simmer 0
        // edge cut 0.7
        // 2 threads#
        // 750 iterations
        // fixed time 0.2
        // Random seed, random.
        System.out.println("Runnnig OpenOrd");
        OpenOrdLayout layout = new OpenOrdLayout(null);
        layout.setGraphModel(graphModel);
        layout.resetPropertiesValues();
        layout.setLiquidStage(24);
        layout.setExpansionStage(75);
        layout.setCooldownStage(1);
        layout.setCrunchStage(0);
        layout.setSimmerStage(0);
        layout.setEdgeCut(0.7f);
        layout.setNumThreads(2);
        layout.setNumIterations(750);
        layout.initAlgo();
        while (layout.canAlgo()) {
            layout.goAlgo();
        }

        // Run modularity
        // do not randomize
        // resolution 1
        System.out.println("Running modularity.");
        
        PartitionController partitionController = Lookup.getDefault().lookup(PartitionController.class);
        Modularity modularity = new Modularity();
        modularity.execute(graphModel, attributeModel);
        // Partition with 'modularity_class', just created by Modularity algorithm
        AttributeColumn modColumn = attributeModel.getNodeTable().getColumn(Modularity.MODULARITY_CLASS);
        Partition p2 = partitionController.buildPartition(modColumn, graph);
        System.out.println(p2.getPartsCount() + " partitions found");
        NodeColorTransformer nodeColorTransformer2 = new NodeColorTransformer();
        nodeColorTransformer2.randomizeColors(p2);
        partitionController.transform(p2, nodeColorTransformer2);

        //Get Centrality
        GraphDistance distance = new GraphDistance();
        distance.setDirected(true);
        distance.execute(graphModel, attributeModel);

        //Rank size by centrality
        AttributeColumn centralityColumn = attributeModel.getNodeTable().getColumn(GraphDistance.BETWEENNESS);
        Ranking centralityRanking = rankingController.getModel().getRanking(Ranking.NODE_ELEMENT, centralityColumn.getId());
        AbstractSizeTransformer sizeTransformer = (AbstractSizeTransformer) rankingController.getModel().getTransformer(Ranking.NODE_ELEMENT, Transformer.RENDERABLE_SIZE);
        sizeTransformer.setMinSize(0);
        sizeTransformer.setMaxSize(20);
        rankingController.transform(centralityRanking,sizeTransformer);

        
        System.out.println("Exporting");

        ExportController ec = Lookup.getDefault().lookup(ExportController.class);
        try {
            ec.exportFile(new File("simple.pdf"));
        } catch (IOException ex) {
            ex.printStackTrace();
            return;
        }
    }
}
