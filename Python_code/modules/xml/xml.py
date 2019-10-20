class task_files:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

def unpack_task_files_xml(doc):
    # Converts an nested xml structure to an object

    task_list = []
    for t in doc.MyoVision_analysis.task_files.task:
        task_list.append(task_files(
                raw_image_file_string=t.raw_image_file_string.cdata,
                results_folder=t.results_folder.cdata))

    return task_list


def unpack_train_classifier_parameters_xml(doc):
    # Converts xml structure to dictionary

    train_classifier_parameters={}
    train_classifier_parameters['input_data_file_string'] = \
        doc.MyoVision_analysis.train_classifier_parameters.input_data_file_string.cdata
    train_classifier_parameters['classification_kernel'] = \
        doc.MyoVision_analysis.train_classifier_parameters.classification_kernel.cdata
    train_classifier_parameters['poly_order'] = \
        int(doc.MyoVision_analysis.train_classifier_parameters.poly_order.cdata)
    train_classifier_parameters['output_classifier_file_string'] = \
        doc.MyoVision_analysis.train_classifier_parameters.output_classifier_file_string.cdata

    return train_classifier_parameters

def unpack_classifier_parameters_xml(doc):
    # Converts xml structure to dictionary
    
    classifier_parameters={}
    classifier_parameters['classification_model_file_string'] = \
        doc.MyoVision_analysis.classifier_parameters.classification_model_file_string.cdata

    return classifier_parameters

def unpack_refine_fibers_parameters_xml(doc):
    # Converts xml structure to dictionary
    
    refine_fibers_parameters={}
    refine_fibers_parameters['max_iterations'] = \
        int(doc.MyoVision_analysis.refine_fibers_parameters.max_iterations.cdata)
    refine_fibers_parameters['sigma'] = \
        float(doc.MyoVision_analysis.refine_fibers_parameters.sigma.cdata)

    return refine_fibers_parameters

def unpack_results_parameters_xml(doc):
    # Converts xml structure to dictionary
    
    results_parameters={}
    results_parameters['results_folder'] = \
        doc.MyoVision_analysis.results_parameters.results_folder.cdata

    return results_parameters


def unpack_image_to_label_parameters_xml(doc):
    # Converts xml structure to dictionary with correct data types

    image_to_label_parameters={}
    image_to_label_parameters['saturation_percent'] = \
        float(doc.MyoVision_analysis.image_to_label_parameters.saturation_percent.cdata)
    image_to_label_parameters['min_object_size'] = \
        int(doc.MyoVision_analysis.image_to_label_parameters.min_object_size.cdata)
    image_to_label_parameters['block_size'] = \
        int(doc.MyoVision_analysis.image_to_label_parameters.block_size.cdata)
    image_to_label_parameters['watershed_distance'] = \
        float(doc.MyoVision_analysis.image_to_label_parameters.watershed_distance.cdata)

    return image_to_label_parameters


def unpack_calculate_blob_parameters_xml(doc):
    # Converts xml structure to dictionary with correct data types

    calculate_blob_parameters={}
    calculate_blob_parameters['display_padding'] = \
        int(doc.MyoVision_analysis.calculate_blob_parameters.display_padding.cdata)
    calculate_blob_parameters['output_blob_base_file_string'] = \
        doc.MyoVision_analysis.calculate_blob_parameters.output_blob_base_file_string.cdata
    calculate_blob_parameters['output_excel_file_string'] = \
        doc.MyoVision_analysis.calculate_blob_parameters.output_excel_file_string.cdata
    calculate_blob_parameters['output_annotated_image_file_string'] = \
        doc.MyoVision_analysis.calculate_blob_parameters.output_annotated_image_file_string.cdata

    return calculate_blob_parameters
