from owlready2 import get_ontology, sync_reasoner, Nothing


def check_ontology_consistency(ontology_path):
    try:
        print(f"Loading ontology from: {ontology_path}")
        onto = get_ontology(ontology_path).load()

        print("Running reasoner...")
        with onto:
            sync_reasoner()  # Reasoning is done here

        # Check for inconsistent individuals
        inconsistent_individuals = list(Nothing.instances())
        if inconsistent_individuals:
            print("\n⚠️ Inconsistencies found! The following individuals are inconsistent:")
            for ind in inconsistent_individuals:
                print(f" - {ind.name} (IRI: {ind.iri})")
        else:
            print("\n✅ Ontology is consistent. No inconsistencies found.")

    except Exception as e:
        print("\n❌ An error occurred during reasoning or loading:")
        print(str(e))


if __name__ == "__main__":
    check_ontology_consistency("../week1/ontology.xml")
