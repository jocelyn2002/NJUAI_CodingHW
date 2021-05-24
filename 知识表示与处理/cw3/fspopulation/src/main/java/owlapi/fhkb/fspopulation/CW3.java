package owlapi.fhkb.fspopulation;

import java.io.InputStream;
import java.util.Collection;

import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.util.DefaultPrefixManager;

import java.util.*;


/**
 * Nanjing University<br>
 * School of Artificial Intelligence<br>
 * KRistal Group<br>
 * 
 * Acknowledgement: with great thanks to Nico for his kindness & useful suggestions in making this project. 
 *
 * This class MUST HAVE A ZERO ARGUMENT CONSTRUCTOR!
 */

public class CW3 {

    private static String NAMESPACE = "http://ai.nju.edu.cn/krp/FamilyHistory#";


    protected CW3() {
        // Do not specify a different constructor to this empty constructor!
    }

    
    protected void populateOntology(OWLOntologyManager manager, OWLOntology ontology, Collection<JobDataBean> beans) {
    	// implement
    	OWLDataFactory df = manager.getOWLDataFactory();
    	
    	OWLClass person = df.getOWLClass(IRI.create(NAMESPACE + "Person"));
    	OWLClass role = df.getOWLClass(IRI.create(NAMESPACE + "Role"));
    	OWLClass source = df.getOWLClass(IRI.create(NAMESPACE + "Source"));
    	OWLClass rolePlayed = df.getOWLClass(IRI.create(NAMESPACE + "RolePlayed"));
    	OWLDataProperty hasBirthYear = df.getOWLDataProperty(IRI.create(NAMESPACE + "hasBithYear"));
    	OWLDataProperty hasYear = df.getOWLDataProperty(IRI.create(NAMESPACE + "hasYear"));
    	OWLDataProperty hasGivenName = df.getOWLDataProperty(IRI.create(NAMESPACE + "hasGivenName"));
    	OWLDataProperty hasSurname = df.getOWLDataProperty(IRI.create(NAMESPACE + "hasSurname"));
    	OWLDataProperty hasMarriedSurname = df.getOWLDataProperty(IRI.create(NAMESPACE + "hasMarriedSurname"));
    	OWLObjectProperty hasRole = df.getOWLObjectProperty(IRI.create(NAMESPACE + "hasRole"));
    	OWLObjectProperty hasSource = df.getOWLObjectProperty(IRI.create(NAMESPACE + "hasSource"));
    	OWLObjectProperty playsRole = df.getOWLObjectProperty(IRI.create(NAMESPACE + "playsRole"));
    	
    	String name="";
    	for (JobDataBean bean: beans) {
    		String surname = bean.getSurname();
    		String givenName = bean.getGivenName(); 
    		if (surname!=null && surname.length()>0) {
    			name = surname+givenName;
    			OWLIndividual tmpPerson = df.getOWLNamedIndividual(IRI.create(NAMESPACE + name));
    			OWLClassAssertionAxiom caa = df.getOWLClassAssertionAxiom(person, tmpPerson);
    			ontology.add(caa);
    		
    			OWLDataPropertyAssertionAxiom dpa = df.getOWLDataPropertyAssertionAxiom(hasSurname, tmpPerson, surname);
    			ontology.add(dpa);
    			dpa = df.getOWLDataPropertyAssertionAxiom(hasGivenName, tmpPerson, givenName);
    			ontology.add(dpa);
    			
    			String marriedSurname=bean.getMarriedSurname();
    			if (marriedSurname!=null && marriedSurname.length()>0) {
    				dpa = df.getOWLDataPropertyAssertionAxiom(hasMarriedSurname, tmpPerson, marriedSurname);
    				ontology.add(dpa);
    			}
    			
    			Integer birthYear = bean.getBirthYear();
    			if (birthYear!= null) {
	    			dpa = df.getOWLDataPropertyAssertionAxiom(hasBirthYear, tmpPerson, birthYear);
	    			ontology.add(dpa);
    			}
    		}
    		else {
    			Integer year = bean.getYear();
    			String soc = bean.getSource();
    			String occupation = bean.getOccupation();
    			OWLIndividual tmpRolePlayed = df.getOWLNamedIndividual(IRI.create(NAMESPACE + name + soc + occupation + year.toString()));
    			OWLClassAssertionAxiom caa = df.getOWLClassAssertionAxiom(person, tmpRolePlayed);
    			ontology.add(caa);
    			
    			OWLDataPropertyAssertionAxiom dpa = df.getOWLDataPropertyAssertionAxiom(hasYear, tmpRolePlayed, year);
    			ontology.add(dpa);
    		}
    	}
    }
    
    
    protected OWLOntology loadOntology(OWLOntologyManager manager, InputStream inputStream){
    	//implement
		OWLOntology o;
		try {
			o = manager.loadOntologyFromOntologyDocument(inputStream);
			return o;
		} catch (OWLOntologyCreationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return null;
    }
    
    protected void saveOntology(OWLOntologyManager manager, OWLOntology ontology, IRI locationIRI){
    	// implement
		try {
			manager.saveOntology(ontology, locationIRI);
		} catch (OWLOntologyStorageException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
    }
}
