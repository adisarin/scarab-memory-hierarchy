#ifndef THREE_C_CLASSIFIER_H
#define THREE_C_CLASSIFIER_H

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
  MISS_COMPULSORY = 0,
  MISS_CAPACITY   = 1,
  MISS_CONFLICT   = 2
} Miss_3C_Type;

void three_c_init(unsigned int total_lines);
Miss_3C_Type three_c_classify(unsigned long long line_addr);

#ifdef __cplusplus
}
#endif

#endif
