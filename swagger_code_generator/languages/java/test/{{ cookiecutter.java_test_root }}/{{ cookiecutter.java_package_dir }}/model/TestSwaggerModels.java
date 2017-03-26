package {{ cookiecutter.java_package }}.model;

import {{ cookiecutter.java_package }}.core.AbstractSwaggerModel;
import {{ cookiecutter.java_package }}.core.SwaggerField;
import org.apache.commons.lang3.reflect.FieldUtils;
import org.junit.Test;
import org.reflections.Reflections;

import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class TestSwaggerModels {
    private void testFieldValidity(Class<? extends AbstractSwaggerModel> cls, String fieldName, SwaggerField swaggerSpecification, Field field) {
        assert Objects.equals(swaggerSpecification.getJavaType(), field.getType()) :
                "TypeError for " + cls.getCanonicalName() + "." + field.getName() + ". Expected " + swaggerSpecification.getJavaType().getCanonicalName() + " found " + field.getType().getCanonicalName();
    }

    private void testModelValidity(Class<? extends AbstractSwaggerModel> cls) throws IllegalAccessException, InstantiationException {
        Map<String, Field> fieldMap = new HashMap<>();
        for (Field field : FieldUtils.getAllFieldsList(cls)) {
            SwaggerField.Annotation annotation = field.getAnnotation(SwaggerField.Annotation.class);
            if (annotation != null) {
                fieldMap.put(annotation.fieldName(), field);
            }
        }
        Map<String, SwaggerField> swaggerFieldMap = new HashMap<>();
        for (Object object : cls.newInstance().getSwaggerFields().entrySet()) {
            final Map.Entry<String, SwaggerField> entry = (Map.Entry<String, SwaggerField>) object;
            swaggerFieldMap.put(entry.getKey(), entry.getValue());
        }

        assert Objects.equals(fieldMap.keySet(), swaggerFieldMap.keySet()) :
                "Not all the " + SwaggerField.class.getCanonicalName() + " are correctly " + SwaggerField.Annotation.class.getCanonicalName() + " annotated. Expected " + swaggerFieldMap.keySet() + " found" + fieldMap.keySet();

        for (String fieldName : swaggerFieldMap.keySet()) {
            testFieldValidity(cls, fieldName, swaggerFieldMap.get(fieldName), fieldMap.get(fieldName));
        }
    }

    @Test
    public void testModelsValidity() {
        Reflections reflections = new Reflections(AbstractSwaggerModel.class.getPackage().getName());
        for (Class<? extends AbstractSwaggerModel> cls : reflections.getSubTypesOf(AbstractSwaggerModel.class)) {
            if (!Modifier.isAbstract(cls.getModifiers())) {
                try {
                    testModelValidity(cls);
                } catch (IllegalAccessException | InstantiationException e) {
                    throw new AssertionError(cls.getCanonicalName() + "is not a POJO class");
                }
            }
        }
    }
}
