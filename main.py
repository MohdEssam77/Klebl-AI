import fitz
from ultralytics import YOLO
from PIL import Image
import os
import json

# Import all specialized processing modules
from plancir.fullimgf import process_plankopf_image
from plancir.plankimg import process_plankopf_image
from plancir.draufsicht import process_draufsicht_image
from plancir.einbauteile import process_einbauteile_image
from plancir.stahl import process_stahl_image
from plancir.vorderansicht import process_vorderansicht_image

def pdf_to_image(pdf_path, page_number=0, output_image_path="output.png"):
    """Converts a page of a PDF file to an image."""
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap()
    pix.save(output_image_path)
    doc.close()
    return output_image_path

def get_processor_for_class(class_name):
    """Returns the appropriate processing function for each class."""
    processors = {
        "Plankopf": process_plankopf_image,
        "Einbauteile": process_einbauteile_image,
        "Stahl": process_stahl_image,
        "Vorderansicht": process_vorderansicht_image,
        "Draufsicht": process_draufsicht_image
    }
    for key, processor in processors.items():
        if key.lower() == class_name.lower():
            return processor
    return None

def process_images_with_fallback(image_path, model_path):
    """Process images with YOLO model and apply specialized processing functions."""
    try:
        model = YOLO(model_path)
        results = model(image_path)
        original_image = Image.open(image_path)
        
        result = results[0]
        boxes = result.boxes
        
        if len(boxes) != 5:
            return process_plankopf_image(image_path)
        
        # Store results by class name
        results_by_class = {}
        
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            
            processor = get_processor_for_class(class_name)
            if not processor:
                continue
            
            # Process the cropped image
            cropped_image = original_image.crop((x1, y1, x2, y2))
            temp_crop_path = f"temp_crop_{class_name}.png"
            cropped_image.save(temp_crop_path)
            
            try:
                json_result = processor(temp_crop_path)
                if isinstance(json_result, str):
                    json_result = json.loads(json_result)
                results_by_class[class_name] = json_result
            finally:
                if os.path.exists(temp_crop_path):
                    os.remove(temp_crop_path)
        
        # Create ordered output
        ordered_result = {}
        desired_order = ["Plankopf", "Einbauteile", "Stahl", "Vorderansicht", "Draufsicht"]
        
        for class_name in desired_order:
            if class_name in results_by_class:
                ordered_result.update(results_by_class[class_name])
        
        return ordered_result
            
    except Exception as e:
        print(f"Error in processing: {str(e)}")
        return process_plankopf_image(image_path)

def main(pdf_path, model_path):
    """Main function to orchestrate the entire process."""
    try:
        output_image_path = pdf_to_image(pdf_path)
        json_result = process_images_with_fallback(output_image_path, model_path)
        
        # Save results
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(json_result, f, indent=2, ensure_ascii=False)
        
        return json_result
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")
        return None

if __name__ == "__main__":
    PDF_PATH = r"plancir\FT_XX_09-001_a_F.pdf"
    MODEL_PATH = "bestmodel.onnx"
    result = main(PDF_PATH, MODEL_PATH)
    
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))