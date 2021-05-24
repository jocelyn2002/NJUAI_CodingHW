package owlapi.msccourse.query;

import java.io.File;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.expression.OWLEntityChecker;
import org.semanticweb.owlapi.expression.ShortFormEntityChecker;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLEntity;
import org.semanticweb.owlapi.model.OWLEquivalentClassesAxiom;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.OWLSubClassOfAxiom;
import org.semanticweb.owlapi.reasoner.InferenceType;
import org.semanticweb.owlapi.reasoner.Node;
import org.semanticweb.owlapi.reasoner.NodeSet;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.util.BidirectionalShortFormProviderAdapter;
import org.semanticweb.owlapi.util.SimpleShortFormProvider;
import org.semanticweb.owlapi.util.mansyntax.ManchesterOWLSyntaxParser;

import com.clarkparsia.pellet.owlapiv3.PelletReasonerFactory;

public class CW5 {

	final OWLOntologyManager man;
	final OWLDataFactory df = OWLManager.getOWLDataFactory();
	final OWLOntology o;
	OWLReasoner r;

	CW5(File file) throws OWLOntologyCreationException {
		// DO NOT CHANGE
		this.man = OWLManager.createOWLOntologyManager();
		this.o = man.loadOntologyFromOntologyDocument(file);
		this.r = new PelletReasonerFactory().createReasoner(o);
		this.r.precomputeInferences(InferenceType.CLASS_HIERARCHY);
	}

	public Set<QueryResult> performQuery(OWLClassExpression exp, QueryType type) {
		/*
		 * Change this method to perform the task
		 */
		System.out.println("Performing Query");
		Set<QueryResult> results = new HashSet<QueryResult>();
		switch (type) {
		case EQUIVALENTCLASSES:
			// Use the reasoner to query for equivalent classes and add the appropriate query results
			Node<OWLClass> eqcs = r.getEquivalentClasses(exp);
			for (OWLClass eq: eqcs.getEntities()) {
				if (eq.toString().equals("owl:Nothing")==false && r.getEquivalentClasses(eq).contains(df.getOWLNothing())==false && results.contains(new QueryResult(eq,true,QueryType.EQUIVALENTCLASSES))==false)
					results.add(new QueryResult(eq,true,QueryType.EQUIVALENTCLASSES));
			}
			break;
		case INSTANCES:
			// Use the reasoner to query for direct and indirect instances (separately) and add the appropriate query results
			for (Node<OWLNamedIndividual> node : r.getInstances(exp, true).getNodes()) {
				for (OWLNamedIndividual direct : node.getEntities()) {
					if (results.contains(new QueryResult(direct,true,QueryType.INSTANCES))==false)
						results.add(new QueryResult(direct,true,QueryType.INSTANCES));
				}
			}
			for (Node<OWLNamedIndividual> node : r.getInstances(exp, false).getNodes()) {
				for (OWLNamedIndividual indirect: node.getEntities()) {
					if (results.contains(new QueryResult(indirect,true,QueryType.INSTANCES))==false && results.contains(new QueryResult(indirect,false,QueryType.INSTANCES))==false)
					results.add(new QueryResult(indirect,false,QueryType.INSTANCES));
				}
			}
			break;
		case SUBCLASSES:
			/// Use the reasoner to query for direct and indirect sub-classes (separately) and add the appropriate query results
			for (Node<OWLClass> node : r.getSubClasses(exp, true).getNodes()) {
				for (OWLClass direct : node.getEntities()) {
					if (direct.toString().equals("owl:Nothing")==false && r.getEquivalentClasses(direct).contains(df.getOWLNothing())==false && results.contains(new QueryResult(direct,true,QueryType.SUBCLASSES))==false) {
						results.add(new QueryResult(direct,true,QueryType.SUBCLASSES));
					}
				}
			}
			for (Node<OWLClass> node : r.getSubClasses(exp, false).getNodes()) {
				for (OWLClass indirect : node.getEntities()) {
					if (indirect.toString().equals("owl:Nothing")==false && r.getEquivalentClasses(indirect).contains(df.getOWLNothing())==false && results.contains(new QueryResult(indirect,true,QueryType.SUBCLASSES))==false && results.contains(new QueryResult(indirect,false,QueryType.SUBCLASSES))==false) {
						results.add(new QueryResult(indirect,false,QueryType.SUBCLASSES));
					}
				}
			}
			break;
		default:
			break;
		}
		return results;
	}
	//自定义函数，用于辅助以下两个函数
	public boolean isValidClass(OWLClassExpression exp, OWLClass cls) {
		boolean b = false;
		for (Node<OWLClass> node : r.getSuperClasses(exp, false).getNodes() )
			if (node.getEntities().contains(cls)) {
				b = true;
				break;
			}
		return b;
	}
	public boolean isValidPizza(OWLClassExpression exp) {
		OWLClass pizza = df.getOWLClass(IRI.create("http://www.co-ode.org/ontologies/pizza/pizza.owl#Pizza"));
		/// IMPLEMENT: Use the reasoner to check whether exp is a valid Pizza expression! Return TRUE if it is.
		return isValidClass(exp,pizza);
	}

	public Set<QueryResult> filterNamedPizzas(Set<QueryResult> results) {
		OWLClass np = df.getOWLClass(IRI.create("http://www.co-ode.org/ontologies/pizza/pizza.owl#NamedPizza"));
		Set<QueryResult> results_filtered = new HashSet<QueryResult>();
		// Add to results filtered only those QueryResults that correspond to NamedPizzas
		for (QueryResult res : results) {
			if (res.type==QueryType.INSTANCES) {
				if (performQuery(np,QueryType.INSTANCES).contains(res))
					results_filtered.add(res);
			}
			else {
				OWLClassExpression exp = parseClassExpression(res.toString());
				if (isValidClass(exp,np)==true)
					results_filtered.add(res);
			}
		}
		return results_filtered;
	}

	public Set<OWLClassExpression> getAllSuperclassExpressions(OWLClass ce) {
		Set<OWLClassExpression> restrictions = new HashSet<OWLClassExpression>();
		Set<OWLClassExpression> addRestrictions = new HashSet<OWLClassExpression>();
		Set<OWLClass> addClasses = new HashSet<OWLClass>();
		// try to think of a way to infer as many restrictions on ce as possible. Tip: You will need to use both the ontology and the reasoner for this task!
		
		for (OWLSubClassOfAxiom ax: o.getSubClassAxiomsForSubClass(ce)) {
			OWLClassExpression exp = ax.getSuperClass();
			if (restrictions.contains(exp)==false) {
				restrictions.add(exp);
			}
		}
		for (OWLEquivalentClassesAxiom ax: o.getEquivalentClassesAxioms(ce)) {
			Set<OWLClassExpression> exps = ax.getClassExpressions();
			for (OWLClassExpression exp : exps)
				if (restrictions.contains(exp)==false) {
					restrictions.add(exp);
				}
		}
//		System.out.println("0   "+restrictions.size());

		int cnt = 0;
		while (true) {
			int oldSize = restrictions.size();
			// 针对restrictions求广义交
			addRestrictions = new HashSet<OWLClassExpression>();
			for (OWLClassExpression exp1 : restrictions) {
				for (OWLClassExpression exp2 : restrictions) {
					OWLClassExpression exp3 = df.getOWLObjectIntersectionOf(exp1,exp2);
					if (addRestrictions.contains(exp3)==false) {
						addRestrictions.add(exp3);
					}
				}
			}
			for (OWLClassExpression exp : addRestrictions) {
				if (restrictions.contains(exp)==false) {
					restrictions.add(exp);
				}
			}
			
			// 对restrictions进行superclass、equivalentclass补全
			addRestrictions = new HashSet<OWLClassExpression>();
			addClasses = new HashSet<OWLClass>();
			for (OWLClassExpression oldExp : restrictions) {
				for (OWLClass c : r.getEquivalentClasses(oldExp).getEntities())
					if (addClasses.contains(c)==false)
						addClasses.add(c);
				for (OWLClass c : r.getSuperClasses(oldExp, false).getFlattened())
					if (addClasses.contains(c)==false)
						addClasses.add(c);
			}
			for (OWLClass c : addClasses) {
				for (OWLSubClassOfAxiom ax: o.getSubClassAxiomsForSubClass(c)) {
					OWLClassExpression exp = ax.getSuperClass();
					if (addRestrictions.contains(exp)==false) {
						addRestrictions.add(exp);
					}
				}
				for (OWLEquivalentClassesAxiom ax: o.getEquivalentClassesAxioms(c)) {
					Set<OWLClassExpression> exps = ax.getClassExpressions();
					for (OWLClassExpression exp : exps)
						if (addRestrictions.contains(exp)==false) {
							addRestrictions.add(exp);
						}
				}
			}
			for (OWLClassExpression exp : addRestrictions) {
				if (restrictions.contains(exp)==false) {
					restrictions.add(exp);
				}
			}
			
			
			
			cnt++;
//			System.out.println(cnt+"   "+restrictions.size());
//			if (restrictions.size()==oldSize)
			if (cnt == 2)
				break;
		}		
		return restrictions;
	}

	public OWLClassExpression parseClassExpression(String sClassExpression) {
		OWLEntityChecker entityChecker = new ShortFormEntityChecker(
				new BidirectionalShortFormProviderAdapter(man, o.getImportsClosure(), new SimpleShortFormProvider()));
		ManchesterOWLSyntaxParser parser = OWLManager.createManchesterParser();
		parser.setOWLEntityChecker(entityChecker);
		parser.setStringToParse(sClassExpression);
		OWLClassExpression exp = parser.parseClassExpression();
		return exp;
	}

}
