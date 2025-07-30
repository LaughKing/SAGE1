#pragma once

#include "operator/base_operator.h"
#include "operator/response.h"
#include "message/multimodal_message_core.h"
#include <string>
#include <vector>
#include <memory>

namespace sage_flow {

// Configuration for vector store sink operations
struct VectorStoreConfig {
    std::string collection_name_;
    size_t batch_size_ = 50;
    bool update_index_ = true;
    std::string index_type_ = "HNSW";
};

/**
 * @brief Vector store sink operator for vector database output
 * 
 * This operator outputs messages to vector databases for embedding storage.
 * Follows the SAGE framework design patterns for sink operators.
 */
class VectorStoreSinkOperator final : public Operator {
 public:
  explicit VectorStoreSinkOperator(VectorStoreConfig config);
  ~VectorStoreSinkOperator() override = default;

  // Prevent copying
  VectorStoreSinkOperator(const VectorStoreSinkOperator&) = delete;
  auto operator=(const VectorStoreSinkOperator&) -> VectorStoreSinkOperator& = delete;

  // Allow moving
  VectorStoreSinkOperator(VectorStoreSinkOperator&&) noexcept = default;
  auto operator=(VectorStoreSinkOperator&&) noexcept -> VectorStoreSinkOperator& = default;

  // Operator interface
  auto process(Response& input_record, int slot) -> bool override;
  auto open() -> void override;
  auto close() -> void override;
  
  // Getter for message count
  auto getMessageCount() const -> size_t { return message_count_; }

 private:
  auto processBatch() -> void;

  VectorStoreConfig config_;
  size_t message_count_{0};
  std::vector<const MultiModalMessage*> batch_messages_;
};

// Factory function
auto CreateVectorStoreSink(const std::string& collection_name, 
                          size_t batch_size = 50, 
                          bool update_index = true) 
    -> std::unique_ptr<VectorStoreSinkOperator>;

}  // namespace sage_flow
