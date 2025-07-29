#pragma once

#include "operator/base_operator.h"
#include "operator/response.h"
#include "message/multimodal_message_core.h"
#include <functional>
#include <memory>

namespace sage_flow {

// Forward declaration - actual definition is in datastream.h
using SinkFunction = std::function<void(const MultiModalMessage&)>;

/**
 * @brief Terminal sink operator for console output
 * 
 * This operator outputs messages to the terminal/console.
 * Follows the SAGE framework design patterns for sink operators.
 */
class TerminalSinkOperator final : public Operator {
 public:
  explicit TerminalSinkOperator(SinkFunction sink_func);
  ~TerminalSinkOperator() override = default;

  // Prevent copying
  TerminalSinkOperator(const TerminalSinkOperator&) = delete;
  auto operator=(const TerminalSinkOperator&) -> TerminalSinkOperator& = delete;

  // Allow moving
  TerminalSinkOperator(TerminalSinkOperator&&) noexcept = default;
  auto operator=(TerminalSinkOperator&&) noexcept -> TerminalSinkOperator& = default;

  auto process(Response& input_record, int slot) -> bool override;
  auto open() -> void override;
  auto close() -> void override;

 private:
  SinkFunction sink_func_;
};

// Factory function
auto CreateTerminalSink(const std::function<void(const MultiModalMessage&)>& sink_func) 
    -> std::unique_ptr<TerminalSinkOperator>;

}  // namespace sage_flow
